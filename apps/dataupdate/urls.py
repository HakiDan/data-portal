from django.urls import path

from . import views

urlpatterns = [
    path('', views.dataupdate, name='dataupdate'),
]