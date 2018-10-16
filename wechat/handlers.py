# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler, WeChatLib
from wechat.models import User, Activity, Ticket
from WeChatTicket import settings
import json
import threading


__author__ = "Epsirom"


class ErrorHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，服务器现在有点忙，暂时不能给您答复 T T')


class DefaultHandler(WeChatHandler):

    def check(self):
        return True

    def handle(self):
        return self.reply_text('对不起，没有找到您需要的信息:(')


class HelpOrSubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('帮助', 'help') or self.is_event('scan', 'subscribe') or \
               self.is_event_click(self.view.event_keys['help'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('help_title'),
            'Description': self.get_message('help_description'),
            'Url': self.url_help(),
        })


class UnbindOrUnsubscribeHandler(WeChatHandler):

    def check(self):
        return self.is_text('解绑') or self.is_event('unsubscribe')

    def handle(self):
        self.user.student_id = ''
        self.user.save()
        return self.reply_text(self.get_message('unbind_account'))


class BindAccountHandler(WeChatHandler):

    def check(self):
        return self.is_text('绑定') or self.is_event_click(self.view.event_keys['account_bind'])

    def handle(self):
        return self.reply_text(self.get_message('bind_account'))


class BookEmptyHandler(WeChatHandler):

    def check(self):
        return self.is_event_click(self.view.event_keys['book_empty'])

    def handle(self):
        return self.reply_text(self.get_message('book_empty'))


class ListActivityHandler(WeChatHandler):

    def check(self):
        return self.is_text('活动', '目录', 'activity', 'list') or \
               self.is_event_click(self.view.event_keys['list_activity'])

    def handle(self):
        return self.reply_single_news({
            'Title': self.get_message('list_title'),
            'Description': self.get_message('list_description'),
            'Url': self.url_list(),
        })


class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text('查票', 'ticket') or \
               self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        print('+++', User.objects.filter(open_id=self.user.open_id)[0])
        studentID = User.objects.filter(open_id=self.user.open_id)[0].student_id
        tickets = Ticket.objects.filter(student_id=studentID)
        
        data = []
        for ticket in tickets:
            uniqueID = ticket.unique_id
            activityName = ticket.activity.name
            data.append({'unique_id': uniqueID, 'name': activityName})

        self.data = json.dumps(data)
        print('+++', data)
        return self.reply_text(self.get_message('ticket_list'))


class GetDetailHandler(WeChatHandler):

    def check(self):
        return self.is_activity_click(self.view.event_keys['book_header'])

    def handle(self):
        id = self.input['EventKey'].split('_')[-1]
        return self.reply_single_news({
            'Title': self.get_message('detail_title'),
            'Description': self.get_message('detail_description'),
            'Url': self.url_activity() + '?id=' + id,
        })


class BookTicketHandler(WeChatHandler):

    def check(self):
        return self.is_contain_key('book') #'抢票') #TODO

    def handle(self):
        actKey = self.input['Content'].split(' ')[-1]
        actModel = Activity.objects.filter(key=actKey)
        if len(actModel) == 0:
            return

        data = dict({
                   'openid': self.user.open_id,
                   'url': self.api_url_book_ticket(),
                   'key': actKey,
               })

        t = threading.Thread(target=WeChatLib.book_ticket, args=(data,))
        t.start()
        return self.reply_text('抢票进行中，请稍等')

        #actKey = self.input['Content'].split(' ')[-1]
        #actModel = Activity.objects.filter(key=actKey)
        #if len(actModel) == 0:
        #    return

        #actModel = actModel[0]
        #res = WeChatLib._http_get(self.api_url_book_ticket() + '?openid=' + self.user.open_id + '&key=' + actKey)
        #rjson = json.loads(res)
        #print('+++++rjson: ', rjson)
        #return self.reply_text('success')


class CancelTicketHandler(WeChatHandler):

    def check(self):
        return self.is_contain_key('cancel') #'退票') #TODO

    def handle(self):
        return
