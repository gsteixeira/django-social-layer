# -*- coding: utf-8 -*-

import mediautils
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from mediautils.views import del_photo

urlpatterns = [
    path("del-photo/<int:pk>/", mediautils.views.del_photo, name="del_photo"),
]
