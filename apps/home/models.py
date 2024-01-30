# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from core.choices import *

# Create your models here.

class Summary(models.Model):
    init_id = models.CharField(max_length=15, blank=True, null=True)
    init_name = models.CharField(max_length=50, blank=True, null=True)
    sub_init_name = models.CharField(max_length=50, blank=True, null=True)
    bumi_status = models.CharField(max_length=50, blank=True, null=True)
    race = models.CharField(max_length=50, blank=True, null=True)
    sector = models.CharField(max_length=200, choices=SECTOR, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    biz_size = models.CharField(max_length=50, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=100, choices=STATUS, blank=True, null=True)
    bene = models.IntegerField(blank=True, null=True)
    allocation = models.FloatField(blank=True, null=True)
    disbursed = models.FloatField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.init_name
    
    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'