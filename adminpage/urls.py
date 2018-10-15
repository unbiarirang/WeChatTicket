# -*- coding: utf-8 -*-
#
from django.conf.urls import url
from adminpage.views import *

__author__ = "Epsirom"


urlpatterns = [
    url(r'^login/?$', LogIn.as_view()),
    url(r'^logout/?$', LogOut.as_view()),
    url(r'^signup/?$', SignUp.as_view()),
    url(r'^activity/list/?$', ListActivity.as_view()),
    url(r'^activity/create/?$', CreateActivity.as_view()),
    url(r'^activity/delete/?$', DeleteActivity.as_view()),
    url(r'^activity/update/?$', UpdateActivity.as_view()),
    url(r'^activity/detail/?$', GetDetail.as_view()),
    url(r'^activity/menu/?$', SetUpMenu.as_view()),
]
