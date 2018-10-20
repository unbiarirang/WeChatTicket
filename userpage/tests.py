import unittest
from userpage.views import *
from wechat.models import Activity, User, Ticket
from wechat.wrapper import WeChatLib
from WeChatTicket.settings import get_url
from collections import namedtuple
from datetime import datetime, timezone, timedelta

openID = 'OPEN_ID'
studentID = '2015080118'
actKey = 'act1'
actName = 'activity1'

class Request():
    def __init__(self):
        self.GET = dict()

    def set_GET(self, key, value):
        self.GET[key] = value

def createUser(openID, studentID):
    user = User(open_id=openID, student_id=studentID)
    user.save()
    return user

def createActivity():
    act = Activity(id=1, name='activity1', key='act1',
                    description='desc1', place='place1',
                    start_time=datetime.now(timezone.utc)+timedelta(days=3),
                    end_time=datetime.now(timezone.utc)+timedelta(days=4),
                    book_start=datetime.now(timezone.utc),
                    book_end=datetime.now(timezone.utc)+timedelta(days=1),
                    total_tickets=100,
                    status=Activity.STATUS_PUBLISHED,
                    pic_url='',
                    remain_tickets=100)
    act.save()
    return act

def createActivityNowBooking():
    act = Activity(name='act_now_booking', key='now_booking',
                    description='desc1', place='place1',
                    start_time=datetime.now(timezone.utc)+timedelta(days=3),
                    end_time=datetime.now(timezone.utc)+timedelta(days=4),
                    book_start=datetime.now(timezone.utc)-timedelta(days=1),
                    book_end=datetime.now(timezone.utc)+timedelta(days=1),
                    total_tickets=100,
                    status=Activity.STATUS_PUBLISHED,
                    pic_url='',
                    remain_tickets=100)
    act.save()
    return act

def createActivityBeforeBooking():
    act = Activity(name='act_before_booking', key='before_booking',
                    description='desc1', place='place1',
                    start_time=datetime.now(timezone.utc)+timedelta(days=3),
                    end_time=datetime.now(timezone.utc)+timedelta(days=4),
                    book_start=datetime.now(timezone.utc)+timedelta(days=1),
                    book_end=datetime.now(timezone.utc)+timedelta(days=2),
                    total_tickets=100,
                    status=Activity.STATUS_PUBLISHED,
                    pic_url='',
                    remain_tickets=100)
    act.save()
    return act

def createActivityAfterBooking():
    act = Activity(name='act_after_booking', key='after_booking',
                    description='desc1', place='place1',
                    start_time=datetime.now(timezone.utc),
                    end_time=datetime.now(timezone.utc)+timedelta(days=1),
                    book_start=datetime.now(timezone.utc)-timedelta(days=2),
                    book_end=datetime.now(timezone.utc)-timedelta(days=1),
                    total_tickets=100,
                    status=Activity.STATUS_PUBLISHED,
                    pic_url='',
                    remain_tickets=100)
    act.save()
    return act
    
def bookTicket(user, act):
    ticket = Ticket(student_id=user.student_id, unique_id=str(datetime.now()), status=Ticket.STATUS_VALID, activity_id=act.id)
    ticket.save()
    return ticket

class TestBookTicket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = createUser(openID, studentID)
        cls.act_now_booking = createActivityNowBooking()
        cls.act_before_booking = createActivityBeforeBooking()
        cls.act_after_booking = createActivityAfterBooking()

    def test_book_ticket(self):
        t = BookTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('key', self.act_now_booking.key)
        t.request = req
        res = t.get()
        return self.assertEqual(res, 1)

    @unittest.expectedFailure
    def test_book_ticket_before(self):
        t = BookTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('key', self.act_before_booking.key)
        t.request = req
        res = t.get()
        return self.assertEqual(res, 1)

    @unittest.expectedFailure
    def test_book_ticket_after(self):
        t = BookTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('key', self.act_after_booking.key)
        t.request = req
        res = t.get()
        return self.assertEqual(res, 1)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.act_now_booking.delete()
        cls.act_before_booking.delete()
        cls.act_after_booking.delete()


class TestUserTicket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = createUser(openID, studentID)
        cls.act = createActivity()
        cls.ticket = bookTicket(cls.user, cls.act)

    def test_user_ticket(self):
        ticket = Ticket.objects.filter(student_id=self.user.student_id, activity=self.act)
        self.assertEqual(len(ticket), 1)
        ticket = ticket[0]
        t = UserTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('ticket', ticket.unique_id)
        t.request = req
        res = t.get()
        return self.assertEqual(res['activityKey'], self.act.key)
        
    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.act.delete()


class TestCancelTicket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = createUser(openID, studentID)
        cls.act_now_booking = createActivityNowBooking()
        cls.act_after_booking = createActivityAfterBooking()

    def test_cancel_ticket(self):
        ticket = bookTicket(self.user, self.act_now_booking)
        t = CancelTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('key', self.act_now_booking.key)
        t.request = req
        res = t.get()
        return self.assertEqual(res, 1)

    @unittest.expectedFailure
    def test_cancel_ticket_not_have(self):
        ticket = bookTicket(self.user, self.act_now_booking)
        t = CancelTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('key', self.act_after_booking.key)
        t.request = req
        res = t.get()

    @unittest.expectedFailure
    def test_cancel_ticket_after_start(self):
        ticket = bookTicket(self.user, self.act_after_booking)
        t = CancelTicket()
        req = Request()
        req.set_GET('openid', self.user.open_id)
        req.set_GET('key', self.act_after_booking.key)
        t.request = req
        res = t.get()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.act_now_booking.delete()
        cls.act_after_booking.delete()
