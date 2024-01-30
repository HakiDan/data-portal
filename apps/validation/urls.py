from django.urls import path
from .views import ValidationView
from . import views

urlpatterns = [
    path("", ValidationView.as_view(), name="validation"),
    path("edit-note/", views.edit_note, name="edit_note"),
    path("validate-data/", views.validate_data, name="validate_data"),
    path("validate-data-comments/", views.validate_data_comments, name="validate_data_comments"),
    path("push-data/", views.push_data, name="push_data"),
    path("push-data-comments/", views.push_data_comments, name="push_data_comments"),
    path("delete-data/", views.delete_data, name="delete_data"),
    path("push-data-report/", views.create_dag_run, name="push_data_report"),
]