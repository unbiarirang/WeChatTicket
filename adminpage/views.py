from django.shortcuts import render
from django.contrib.auth.models import User
from wechat.models import Activity
from django.contrib.auth import authenticate 
from codex.baseview import APIView
from codex.baseerror import ValidateError
from django.http import HttpResponse
from django.core import serializers
from django.utils import timezone
from wechat.views import CustomWeChatView
import json
import time
import dateutil.parser

cache = 1 
# TODO: session management
class LogIn(APIView):
    def get(self):
        global cache
        if cache == 0:
            raise ValidateError('You should login first') 
    
    def post(self):
        global cache
        cache = 1

        data = json.loads(self.request.body.decode('utf8'))
        username = data['username']
        password = data['password']

        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidateError('Invalid user name or password.')


class LogOut(APIView):
    def post(self):
        global cache
        cache = 0
    

# TODO
class SignUp(APIView):
    def get(self):
        pass

    def post(self):
        pass


class ListActivity(APIView):
    def get(self):
        actModels = json.loads(serializers.serialize('json', Activity.objects.all()))

        activities = []
        for m in actModels:
            activity = m['fields']
            activity['id'] = m['pk']
            activity['currentTime'] = time.time()
            for newKey, oldKey in [('startTime', 'start_time'), ('endTime', 'end_time'),
                                   ('bookStart', 'book_start'), ('bookEnd', 'book_end')]:
                activity[newKey] = dateutil.parser.parse(activity[oldKey]).timestamp()
            activities.append(activity)
            
        return activities
    

class CreateActivity(APIView):
    
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        data['remainTickets'] = data['totalTickets']

        camelList = ['startTime', 'endTime', 'totalTickets', 'remainTickets', \
                     'bookStart', 'bookEnd', 'picUrl'] 
        underList = ['start_time', 'end_time', 'total_tickets', 'remain_tickets', \
                     'book_start', 'book_end', 'pic_url']
        for index, key in enumerate(camelList):
            if key in data:
                data[underList[index]] = data[key]
                data.pop(key, None)

        activity = Activity(**data)
        activity.save()


class UpdateActivity(APIView):

    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        data['remainTickets'] = data['totalTickets'] 

        camelList = ['startTime', 'endTime', 'totalTickets', 'remainTickets', \
                     'bookStart', 'bookEnd', 'picUrl'] 
        underList = ['start_time', 'end_time', 'total_tickets', 'remain_tickets', \
                     'book_start', 'book_end', 'pic_url']
        for index, key in enumerate(camelList):
            if key in data:
                data[underList[index]] = data[key]
                data.pop(key, None)

        uselessList = ['bookStart-month', 'bookStart-minute', 'bookStart-day', \
                       'bookStart-hour', 'bookStart-year', 'currentTime']
        for key in uselessList:
            data.pop(key, None)
        print('+++data:', data)

        activity = Activity.objects.filter(id=data['id'])[0]
        activity.delete()

        newActivity = Activity(**data)
        newActivity.save()
        

class DeleteActivity(APIView):

    def post(self):
        delID = json.loads(self.request.body.decode('utf-8'))['id']
        Activity.objects.filter(id=delID).delete()


class GetDetail(APIView):

    def get(self):
        activityID = self.request.GET.get('id', '')
        actModel = Activity.objects.filter(id=activityID)
        if len(actModel) != 0:
            activity = json.loads(serializers.serialize('json', actModel))[0]['fields']
            activity['currentTime'] = time.time()
            for newKey, oldKey in [('startTime', 'start_time'), ('endTime', 'end_time'),
                                   ('bookStart', 'book_start'), ('bookEnd', 'book_end')]:
                activity[newKey] = dateutil.parser.parse(activity[oldKey]).timestamp()
            return activity


class SetUpMenu(APIView):

    def get(self):
        currentMenu = CustomWeChatView.lib.get_wechat_menu()
        actButtons = []
        for btn in currentMenu:
            if btn['name'] == '抢票':
                actButtons = btn.get('sub_button', list())

        activities = []
        for idx, btn in enumerate(actButtons):
            activity = dict()
            activity['id'] = btn['key'].split('_')[-1]
            activity['name'] = btn['name']
            activity['menuIndex'] = idx + 1
            activities.append(activity)

        return activities

    
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        idList = data['ids']
        nameList = data['names']

        activities = []
        for idx, id in enumerate(idList):
            activity = Activity()
            activity.id = id
            activity.name = nameList[idx]
            activities.append(activity)

        print('+++', activities)
        CustomWeChatView.update_menu(activities)



