from django.urls import path
from apps.masterlist import views
from . import views
from .views import (MasterlistUpload, MasterlistView, 
                    MasterlistModifyView, MasterlistUpdate, 
                    BulkUpdateInit)
from apps.authentication.views import add_agency

urlpatterns = [
    path("", MasterlistView.as_view(), name="masterlist"),
    path("modify-list/", MasterlistModifyView.as_view(), name="modifylist"),
    path("list-add/", MasterlistUpload.as_view(), name="listadd"),
    path("modify-list/list-edit/<int:pk>", MasterlistUpdate.as_view(), name="listedit"),
    path("add-option", add_agency, name="add_agency"),
    path("bulk-update-init", BulkUpdateInit.as_view(), name="bulk_update_init"),
    path('cancel-submission-masterlist/', views.cancel_submission_masterlist, name='cancel_submission_masterlist'),
    path('submit-masterlist/', views.submit_masterlist, name='submit_masterlist'),
]