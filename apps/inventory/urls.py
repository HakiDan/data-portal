from django.urls import path
from apps.inventory import views
from . import views

urlpatterns = [
    path("", views.inventory, name="inventory"),
    path("additem", views.add, name="additem"),
    path("edititem", views.edit, name="edititem"),
]