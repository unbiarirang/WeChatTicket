# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from userpage.views import *


__author__ = "Epsirom"


urlpatterns = [
    url(r'^bind/?$', UserBind.as_view()),
    url(r'^help/?$', UserHelp.as_view()),
    url(r'^list/?$', ListActivity.as_view()),
    url(r'^activity/detail/?$', GetDetail.as_view()),
#    url(r'^ticket/list?$', ListTicket.as_view()),
    url(r'^ticket/detail/?$', UserTicket.as_view()),
    url(r'^ticket/book/?$', BookTicket.as_view()), 
    url(r'^ticket/cancle/?$', CancelTicket.as_view()),
]
