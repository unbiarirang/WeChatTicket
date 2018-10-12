# -*- coding: utf-8 -*-
#
from django.conf.urls import url
from adminpage.views import *

__author__ = "Epsirom"


urlpatterns = [
    url(r'^signup/?', SignUp.as_view()),
]
