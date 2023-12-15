# -*- coding: utf-8 -*-

from django.urls import path
from mediautils.views import del_photo

urlpatterns = [
    path("del-photo/<int:pk>/", del_photo, name="del_photo"),
]
