from django.urls import path
from apps.upload import views
from . import views
from apps.datacleaning.views import DataCleaning

urlpatterns = [
    path("", DataCleaning.as_view(), name="datacleaning"),
    path('submit-value/', views.submitValue, name='submitValue'),
]
