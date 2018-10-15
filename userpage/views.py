from codex.baseerror import *
from codex.baseview import APIView
from codex.baseerror import ValidateError
from WeChatTicket.views import StaticFileView
from wechat.models import User, Activity
from django.core import serializers
import re
import json
import time
import dateutil.parser



class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        studentID = self.input['student_id']
        p = re.compile('^20[0-9]{8}$')
        if p.match(studentID) is None:
            raise ValidateError('Invalid student info.')

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()


class UserHelp(StaticFileView):

    def get(self):
        return self.get_file('/help')


class ListActivity(APIView):
    def get(self):
        actObjs = json.loads(serializers.serialize('json', Activity.objects.all()))

        activities = []
        for o in actObjs:
            activity = o['fields']
            activity['id'] = o['pk']
            activities.append(activity)
            
        return activities


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


#TODO
class UserTicket(APIView):
    
    def get(self):
        raise NotImplementedError('You should implement UserTicket')

#TODO
class Ticketing(APIView):
    def get(self):
        raise NotImplementedError('You should implement Ticketing')

    def post(self):
        raise NotImplementedError('You should implement Ticheting')

