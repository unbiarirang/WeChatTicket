from django.shortcuts import render
from django.contrib.auth.models import User
from wechat.models import Activity, Ticket
from django.contrib.auth import authenticate 
from codex.baseview import APIView
from codex.baseerror import ValidateError, NotAvailableError, DuplicateError
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
from datetime import datetime

class LogIn(APIView):
    def get(self):
        if self.request.session['login'] == False:
            raise ValidateError('You should login first') 
    
    def post(self):
        self.request.session['login'] = True

        data = json.loads(self.request.body.decode('utf8'))
        username = data['username']
        password = data['password']

        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidateError('Invalid user name or password.')
        else:
            return user

class LogOut(APIView):
    def post(self):
        self.request.session['login'] = False 
        return False

class ListActivity(APIView):
    def get(self):
        actModels = json.loads(serializers.serialize('json', Activity.objects.all()))

        activities = []
        for m in actModels:
            activity = m['fields']
            activity['id'] = m['pk']
            activity['currentTime'] = timezone.now().timestamp()
            for newKey, oldKey in [('startTime', 'start_time'), ('endTime', 'end_time'),
                                   ('bookStart', 'book_start'), ('bookEnd', 'book_end')]:
                try:
                    activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%SZ").timestamp()
                except ValueError: # for test
                    activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()

            activities.append(activity)
            
        return activities
    

class CreateActivity(APIView):
    
    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))

        actModels = Activity.objects.filter(name=data['name'])
        if len(actModels) != 0:
            raise DuplicateError('Duplicated activity name!')

        actModels = Activity.objects.filter(key=data['key'])
        if len(actModels) != 0:
            raise DuplicateError('Duplicated activity key!')

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
        if len(actModel) == 0:
            return

        activity = json.loads(serializers.serialize('json', actModel))[0]['fields']
        actModel = actModel[0]
        activity['id'] = actModel.id
        activity['currentTime'] = timezone.now().timestamp()
        activity['totalTickets'] = actModel.total_tickets
        activity['bookedTickets'] = actModel.total_tickets - actModel.remain_tickets
        ticketModels = Ticket.objects.filter(activity=actModel, status=Ticket.STATUS_USED)
        activity['usedTickets'] = len(ticketModels)
        for newKey, oldKey in [('startTime', 'start_time'), ('endTime', 'end_time'),
                               ('bookStart', 'book_start'), ('bookEnd', 'book_end')]:
            try:
                activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%SZ").timestamp()
            except ValueError:
                activity[newKey] = datetime.strptime(activity[oldKey], "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()
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
                       'bookStart-hour', 'bookStart-year', 'currentTime', 'usedTickets', 'bookedTickets']
        for key in uselessList:
            data.pop(key, None)

        activity = Activity.objects.filter(id=data['id'])[0]
        activity.delete()

        newActivity = Activity(**data)
        newActivity.save()
        return 1


class SetUpMenu(APIView):

    def get(self):
        currentMenu = CustomWeChatView.lib.get_wechat_menu()
        actButtons = []
        for btn in currentMenu:
            if btn['name'] == '抢票':
                actButtons = btn.get('sub_button', list())

        activities = []
        actIDs = []
        for idx, btn in enumerate(actButtons):
            activity = dict()
            activity['id'] = btn['key'].split('_')[-1]
            actIDs.append(int(activity['id']))
            activity['name'] = btn['name']
            activity['menuIndex'] = idx + 1
            activities.append(activity)

        actModels = Activity.objects.filter(book_end__gt=timezone.now())
        for actModel in actModels:
            if actModel.id not in actIDs:
                print('+++', actModel.id)
                activity = dict()
                activity['id'] = actModel.id
                activity['name'] = actModel.name
                activity['menuIndex'] = 0
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
        full_path = settings.get_url('/static/media/' + path)
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
