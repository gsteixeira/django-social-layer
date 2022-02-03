#-*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

import mediautils
from mediautils.views import del_photo


urlpatterns = [
    path('del-photo/<int:pk>/', mediautils.views.del_photo, name='del_photo'),
    ]
