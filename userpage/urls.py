# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from userpage.views import *


__author__ = "Epsirom"


urlpatterns = [
    url(r'^user/bind/?$', UserBind.as_view()),
    url(r'^help/?$', UserHelp.as_view()),
    url(r'^activity/?$', GetActivityDetail.as_view()),
    url(r'^ticket/detail/?$', UserTicket.as_view()),
    url(r'^ticket/book/?$', BookTicket.as_view()), 
    url(r'^ticket/cancel/?$', CancelTicket.as_view()),
]
