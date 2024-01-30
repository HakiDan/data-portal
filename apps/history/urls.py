# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.history import views

urlpatterns = [
    path('', views.history_submission, name='history'),
    path('downloadfile-accepted/', views.downloadfile_accepted, name='downloadfile_accepted'),
    path('downloadfile-rejected/', views.downloadfile_rejected, name='downloadfile_rejected'),
]
