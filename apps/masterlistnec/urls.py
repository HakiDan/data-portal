from django.urls import path
from .views import (MasterlistNECView, MasterlistNECModifyView, 
                    MasterlistNECUpdate, MasterlistNECUpload)
from apps.authentication.views import add_agency

urlpatterns = [
    path("", MasterlistNECView.as_view(), name="masterlist_nec"),
    path("list-add/", MasterlistNECUpload.as_view(), name="listadd_nec"),
    path("modify-list-nec/", MasterlistNECModifyView.as_view(), name="modifylist_nec"),
    path("modify-list-nec/list-edit-nec/<int:pk>", MasterlistNECUpdate.as_view(), name="listedit_nec"),
    path("add-option-nec", add_agency, name="add_agency"),
]