from django.urls import path
from apps.upload import views
from . import views

urlpatterns = [
    path("", views.faq, name="faq"),
    path("download-faq/<str:file_name>/", views.download_faq, name="download_faq"),
]