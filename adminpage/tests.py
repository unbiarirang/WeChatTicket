import unittest
from datetime import datetime, timedelta, timezone
from wechat.models import Activity, User, Ticket
from wechat.wrapper import WeChatLib
from WeChatTicket.settings import get_url
from userpage.views import *
from adminpage.views import *
import json
from datetime import datetime, timezone


class Request():
    def __init__(self):
        self.body = dict()
        self.session = dict()
    def set_GET(self,key,value):
        self.body[key] = value
    def set_session(self,key,value):
        self.session[key] = value

class RequestGET():
    def __init__(self):
        self.GET = dict()
    def set_GET(self,key,value):
        self.GET[key] = value

def  myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()

class TestLogIn(unittest.TestCase):
    def setUp(self):
        User.objects.create_superuser('admin','mail@mails.com','thudmteam123')
        
    def test_login(self):
        req = Request()
        guest  = LogIn()
        req.set_session('Login',False)
        req.set_GET('username','admin')
        req.set_GET('password','thudmteam123')
        req.body = json.dumps(req.body,default = myconverter)
        req.body = req.body.encode('gbk')
        guest.request = req
        return self.assertEqual('admin',guest.post().username)


class TestLogOut(unittest.TestCase):
    def test_logout(self):
        req = Request()
        req.set_session('login',True)
        guest2 = LogOut()
        guest2.request = req
        return self.assertEqual(0,guest2.post())

class TestActivity(unittest.TestCase):
    def setUp(self):
        act1 = Activity(id=1, name='activity1', key='act1',
                        description='desc1', place='place1',
                        start_time=datetime.now(timezone.utc)+timedelta(days=3),
                        end_time=datetime.now(timezone.utc)+timedelta(days=4),
                        book_start=datetime.now(timezone.utc),
                        book_end=datetime.now(timezone.utc)+timedelta(days=1),
                        total_tickets=100,
                        status=Activity.STATUS_PUBLISHED,
                        pic_url='',
                        remain_tickets=100)
        act1.save()
        print('act1 created!')
    
    def test_list_activity(self):
        activities = ListActivity().get()
        return self.assertEqual(len(activities), Activity.objects.all().count())
    
    def test_create_activity(self):
        origin_cnt = Activity.objects.filter(id=2).count()
        create_act = CreateActivity()
        req = Request()
        req.set_GET('id',2)
        req.set_GET('name','activity2')
        req.set_GET('key','act2')
        req.set_GET('description','desc1')
        req.set_GET('place','place1')
        req.set_GET('startTime',datetime.now(timezone.utc)+timedelta(days=3))
        req.set_GET('endTime',datetime.now(timezone.utc)+timedelta(days=4))
        req.set_GET('bookStart',datetime.now(timezone.utc))
        req.set_GET('bookEnd',datetime.now(timezone.utc)+timedelta(days=1))
        req.set_GET('totalTickets',100)
        req.set_GET('status',Activity.STATUS_PUBLISHED)
        req.set_GET('picUrl','')
        req.set_GET('remainTickets',100)
        req.body = json.dumps(req.body,default = myconverter)
        req.body = req.body.encode('gbk')
        create_act.request = req
        create_act.post()
        return self.assertEqual(origin_cnt + 1,Activity.objects.filter(id=2).count())

    def test_delete_activity(self):
        origin_cnt = Activity.objects.filter(id=1).count()
        info = DeleteActivity()
        req = Request()
        req.set_GET('id',1)
        req.body = json.dumps(req.body)
        req.body = req.body.encode('gbk')
        info.request = req
        info.post()
        return self.assertEqual(origin_cnt - 1,Activity.objects.filter(id=1).count()) 
    
    def test_get_detail_get(self):
        req = RequestGET()
        guest = GetDetail()
        req.set_GET('id',1)
        guest.request = req
        return self.assertEqual(guest.get()['key'],Activity.objects.filter(id=1)[0].key)
    def test_get_detail_post(self):
        req = Request()
        req2 = RequestGET()
        req2.set_GET('id',1)
        info = GetDetail()
        Edit = GetDetail()
        info.request = req2
     
        req.set_GET('id',info.get()['id'])
        req.set_GET('startTime',info.get()['start_time'])
        req.set_GET('endTime',info.get()['end_time'])
        req.set_GET('bookStart',info.get()['book_start'])
        req.set_GET('bookEnd',info.get()['book_end'])
        req.set_GET('picUrl',info.get()['pic_url'])
        req.set_GET('description','work normally')
        req.set_GET('remainTickets',info.get()['remain_tickets'])
        req.set_GET('totalTickets',info.get()['total_tickets'])
        req.set_GET('status',1)
        req.body = json.dumps(req.body)
        req.body = req.body.encode('gbk')
        Edit.request = req
     
        return self.assertEqual(Edit.post(),1)


if __name__ == '__main__':
    unittest.main()

