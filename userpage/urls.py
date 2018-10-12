# -*- coding: utf-8 -*-
#
from django.conf.urls import url

from userpage.views import *


__author__ = "Epsirom"


urlpatterns = [
    url(r'^bind/?$', UserBind.as_view()),
    url(r'^help/?$', UserHelp.as_view()),
    #url(r'^list/?$', ListActivities.as_view()), # return news format
    url(r'^ticket/?$', UserTicket.as_view()),    # return html
    url(r'^activity/?$', Ticketing.as_view()), 
]
