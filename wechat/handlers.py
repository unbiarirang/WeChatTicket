# -*- coding: utf-8 -*-
#
from wechat.wrapper import WeChatHandler, WeChatLib
from wechat.models import Activity, Ticket
from WeChatTicket import settings
from django.utils import timezone
import json
import time
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
        return self.is_text('抢啥', '活动', '目录', 'activity', 'list') or \
               self.is_event_click(self.view.event_keys['list_activity'])

    def handle(self):
        actModels = Activity.objects.filter(status=Activity.STATUS_PUBLISHED,
                                            book_end__gt=timezone.now())

        newsList = []
        for actModel in actModels:
            news = dict({
                'Title': actModel.name,
                'Description': actModel.description,
                'PicUrl': actModel.pic_url,
                'Url': self.url_activity() + '?id=' + str(actModel.id)
            })
            newsList.append(news)

        if len(newsList) == 0:
            return self.reply_text(self.get_message('book_empty'))
        return self.reply_news(newsList)


class BookTicketButtonHandler(WeChatHandler):

    def check(self):
        return self.is_activity_click(self.view.event_keys['book_header'])

    def handle(self):
        actID = self.input['EventKey'].split('_')[-1]
        actModel = Activity.objects.filter(id=actID)
        if len(actModel) == 0:
            return self.reply_text('活动不存在')
        actModel = actModel[0]

        data = dict({
                   'openid': self.user.open_id,
                   'url': self.api_url_book_ticket(),
                   'key': actModel.key,
                   'action': 'book',
               })

        t = threading.Thread(target=WeChatLib.handle_ticket, args=(data,))
        t.start()
        return self.reply_text('抢票进行中，请稍等')


class BookTicketHandler(WeChatHandler):

    def check(self):
        return self.is_contain_key('book') #'抢票') #TODO

    def handle(self):
        actKey = self.input['Content'].split(' ')[-1]
        actModel = Activity.objects.filter(key=actKey)
        if len(actModel) == 0:
            return self.reply_text('活动不存在')

        data = dict({
                   'openid': self.user.open_id,
                   'url': self.api_url_book_ticket(),
                   'key': actKey,
                   'action': 'book',
               })

        t = threading.Thread(target=WeChatLib.handle_ticket, args=(data,))
        t.start()
        return self.reply_text('请稍等')


class GetTicketHandler(WeChatHandler):

    def check(self):
        return self.is_text('查票', 'ticket') or \
               self.is_contain_key('取票') or \
               self.is_event_click(self.view.event_keys['get_ticket'])

    def handle(self):
        studentID = self.user.student_id
        ticketModels = None
        if self.is_contain_key('取票') and len(self.input['Content'].split(' ')) == 2:
            activityID = Activity.objects.filter(key=self.input['Content'].split(' ')[-1])
            ticketModels = Ticket.objects.filter(activity_id=activityID, status=Ticket.STATUS_VALID)
        else:
            ticketModels = Ticket.objects.filter(student_id=studentID, status=Ticket.STATUS_VALID)
        
        newsList = []
        for ticketModel in ticketModels:
            news = dict({
                'Title': ticketModel.activity.name,
                'Description': ticketModel.activity.description,
                'PicUrl': ticketModel.activity.pic_url,
                'Url': self.url_ticket() + '?openid=' + self.user.open_id + '&ticket=' + ticketModel.unique_id
            })
            newsList.append(news)

        return self.reply_news(newsList)


class CancelTicketHandler(WeChatHandler):

    def check(self):
        return self.is_contain_key('cancel') #'退票') #TODO

    def handle(self):
        actKey = self.input['Content'].split(' ')[-1]
        actModel = Activity.objects.filter(key=actKey)
        if len(actModel) == 0:
            return self.reply_text('活动不存在')

        data = dict({
                   'openid': self.user.open_id,
                   'url': self.api_url_cancel_ticket(),
                   'key': actKey,
                   'action': 'cancel',
               })

        t = threading.Thread(target=WeChatLib.handle_ticket, args=(data,))
        t.start()
        return self.reply_text('请稍等')
