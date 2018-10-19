import unittest
from datetime import datetime, timedelta, timezone
from wechat.models import Activity, User, Ticket
from wechat.wrapper import WeChatLib
from WeChatTicket.settings import get_url
from userpage.views import *
from adminpage.views import *
import json
from datetime import datetime, timezone

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
        return self.assertEqual(len(activities), 1)


if __name__ == '__main__':
    unittest.main()

