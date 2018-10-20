from codex.baseerror import *
from codex.baseview import APIView
from codex.baseerror import ValidateError, NotAvailableError, TransactionError, NotBindError, NotExistError
from WeChatTicket.views import StaticFileView
from wechat.models import User, Activity, Ticket
from django.core import serializers
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils import timezone
import re
import json
import time
import uuid
from datetime import datetime 


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


class GetActivityDetail(APIView):

    def get(self):
        activityID = self.request.GET.get('id', '')
        actModel = Activity.objects.filter(id=activityID)
        if len(actModel) == 0:
            return

        activity = json.loads(serializers.serialize('json', actModel))[0]['fields']
        activity['currentTime'] = timezone.now().timestamp()
        activity['totalTickets'] = activity['total_tickets']
        activity['remainTickets'] = activity['remain_tickets']
        for newKey, oldKey in [('startTime', 'start_time'), ('endTime', 'end_time'), ('bookStart', 'book_start'), ('bookEnd', 'book_end')]:
            try:
                activity[newKey] = datetime.strptime(activity[oldKey], '%Y-%m-%dT%H:%M:%SZ').timestamp()
            except ValueError:
                activity[newKey] = datetime.strptime(activity[oldKey], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        return activity


class UserTicket(APIView):
    
    def get(self):
        openID = self.request.GET.get('openid', '')
        ticketID = self.request.GET.get('ticket', '')
 
        ticketModel = Ticket.objects.filter(unique_id=ticketID)
        if len(ticketModel) == 0:
            raise NotExistError('Ticekt not exist')

        ticketModel = ticketModel[0]
        ticket = dict()
        ticket['uniqueId'] = ticketID
        ticket['status'] = ticketModel.status

        activityID = ticketModel.activity_id
        activity = Activity.objects.filter(id=activityID)[0]

        ticket['ativityName'] = activity.name
        ticket['place'] = activity.place
        ticket['activityKey'] = activity.key
        ticket['startTime'] = activity.start_time.timestamp()
        ticket['endTime'] = activity.end_time.timestamp()
        ticket['currentTime'] = timezone.now().timestamp()

        return ticket


class BookTicket(APIView):

    def get(self):
        openID = self.request.GET.get('openid', '')
        actKey = self.request.GET.get('key', '')

        userModel = User.objects.all().filter(open_id=openID)
        if len(userModel) == 0:
            raise NotExistError('User not exist')
        
        userModel = userModel[0]
        if userModel.student_id == '':
            raise NotBindError('You should bind student id.')

        try:
            with transaction.atomic(): # Transaction
                # decrease remain ticket count in Activity table
                actModel = Activity.objects.filter(key=actKey, status=Activity.STATUS_PUBLISHED)
                if len(actModel) == 0:
                    raise NotAvailableError('Activity not exists')

                actModel = actModel[0]
                if (actModel.book_start.timestamp() > timezone.now().timestamp()) or (actModel.book_end.timestamp() < timezone.now().timestamp()):
                    raise NotAvailableError('Ticketing is not in progress')

                if actModel.remain_tickets <= 0:
                    raise NotAvailableError('No ticket')

                actModel.remain_tickets -= 1
                actModel.save()

                # insert new ticket to Activity table
                ticketID = str(uuid.uuid4()) + openID[-5:]
                ticketModel = Ticket(student_id=userModel.student_id,
                                     unique_id=ticketID,
                                     activity=actModel,
                                     status=Ticket.STATUS_VALID)
                ticketModel.save()

        except IntegrityError:
            raise TransactionError('Please try again')

        return 1


class CancelTicket(APIView): 
    def get(self):
        openID = self.request.GET.get('openid', '')
        actKey = self.request.GET.get('key', '')

        userModel = User.objects.all().filter(open_id=openID)
        if len(userModel) == 0:
            raise NotExistError('User not exist')
        
        userModel = userModel[0]
        if userModel.student_id == '':
            raise NotBindError('You should bind student id.')

        try:
            with transaction.atomic(): # Transaction
                # increase remain ticket count of the Activity
                actModel = Activity.objects.filter(key=actKey)
                if len(actModel) == 0:
                    raise NotAvailableError('Activity not exists')

                actModel = actModel[0]
                # delete ticket in Ticket table
                ticketModel = Ticket.objects.filter(student_id=userModel.student_id,
                                                    activity_id=actModel.id,
                                                    status=Ticket.STATUS_VALID)
                if len(ticketModel) == 0:
                    raise NotAvailableError("You don't have the ticket")

                if actModel.start_time < timezone.now():
                    raise NotAvailableError('You cannot cancel a ticket after the activity starts')

                ticketModel = ticketModel[0]
                ticketModel.status = Ticket.STATUS_CANCELLED
                ticketModel.save()

                actModel.remain_tickets += 1
                actModel.save()


        except IntegrityError:
            raise TransactionError('Please try again')

        return 1

