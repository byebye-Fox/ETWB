#!/usr/bin/env python
# coding:utf-8
"""
Name : urls
Author  : anne
Time    : 2020/2/26 8:34 上午
Desc:
"""
from django.urls import path

from . import views

urlpatterns = [
    path('',views.show_introduction,name="introduction"),
    path('introduction', views.show_introduction, name='introduction'),

]