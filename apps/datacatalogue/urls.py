from django.urls import path
from apps.datacatalogue import views
from . import views

urlpatterns = [
    path("", views.datacatalogue, name="datacatalogue"),
    path("initcatalogue/", views.initcatalogue, name="initcatalogue"),
    path("tempcatalogue/", views.tempcatalogue, name="tempcatalogue"),
]
