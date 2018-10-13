from django.shortcuts import render
from django.contrib.auth.models import User
from wechat.models import Activity
from django.contrib.auth import authenticate 
from codex.baseview import APIView
from codex.baseerror import BaseError
from django.http import HttpResponse
from django.core import serializers
import json
import datetime

cache =1 
# TODO: session management
class LogIn(APIView):
    def get(self):
        global cache
        if cache == 0:
            raise BaseError(401, 'You should login first') 
    
    def post(self):
        global cache
        cache = 1

        data = json.loads(self.request.body.decode('utf8'))
        username = data['username']
        password = data['password']

        user = authenticate(username=username, password=password)
        if user is None:
            raise BaseError(403, 'Invalid user name or password.')


class LogOut(APIView):
    def post(self):
        global cache
        cache = 0
    

# TODO
class SignUp(APIView):
    def get(self):
        pass
    
    def post(self):
        raise NotImplementedError('You should implement SignUp')


class ListActivity(APIView):
    def get(self):
        actObjs = json.loads(serializers.serialize('json', Activity.objects.all()))

        activities = []
        for o in actObjs:
            activity = o['fields']
            activity['id'] = o['pk']
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
        data['id'] += 1 #temp
        #activity.delete()

        newActivity = Activity(**data)
        newActivity.save()
        

class DeleteActivity(APIView):

    def post(self):
        delID = json.loads(self.request.body.decode('utf-8'))['id']
        Activity.objects.filter(id=delID).delete()


class GetDetail(APIView):

    def get(self):
        activityID = self.request.GET.get('id', '')
        activity = Activity.objects.filter(id=activityID)
        if len(activity) != 0:
            activityObj = json.loads(serializers.serialize('json', activity))[0]['fields']
            print('+++time: ', activityObj['start_time'])
            activityObj['currentTime'] = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat() 
            return activityObj


# TODO
class SetUpActivities(APIView):
    def get(self):
        raise NotImplementedError('You should implement SignUp')
    
    def post(self):
        raise NotImplementedError('You should implement SignUp')

