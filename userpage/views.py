from codex.baseerror import *
from codex.baseview import APIView
from WeChatTicket.views import StaticFileView

from wechat.models import User


class UserBind(APIView):

    def validate_user(self):
        # TODO:
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """

        raise NotImplementedError('You should implement UserBind.validate_user method')

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

