from django.shortcuts import render
from django.contrib.auth.models import User
from wechat.models import Activity, Ticket
from django.contrib.auth import authenticate 
from codex.baseview import APIView
from codex.baseerror import ValidateError, NotAvailableError
from django.http import HttpResponse
from django.core import serializers
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
from wechat.views import CustomWeChatView
from WeChatTicket import settings
import os
import json
import time
from datetime import datetime

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
                try:
                    activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%SZ").timestamp()
                except ValueError: # for testcase
                    activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()

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
                activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%SZ").timestamp()
            return activity

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

        activity = Activity.objects.filter(id=data['id'])[0]
        activity.delete()

        newActivity = Activity(**data)
        newActivity.save()


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

        CustomWeChatView.update_menu(activities)


class UploadImage(APIView):
    
    def post(self):
        image = self.request.FILES['image']
        path = default_storage.save(image.name, ContentFile(image.read()))
        full_path = settings.get_url('images/' + path)
        return full_path


class CheckIn(APIView):

    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        actID = data['actId']
        studentID = data['studentId']
        
        ticketModel = Ticket.objects.filter(student_id=studentID,
                                            activity_id=actID,
                                            status=Ticket.STATUS_VALID)
        if len(ticketModel) == 0:
            raise NotAvailableError('Ticket does not exist or is unavailable')

        ticketModel = ticketModel[0]
        ticketModel.status = Ticket.STATUS_USED
        ticketModel.save()
        
        resData = dict()
        resData['studentId'] = studentID
        resData['ticket'] = ticketModel.unique_id
        return resData
