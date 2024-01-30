from django.urls import path
from apps.report import views
from . import views

urlpatterns = [
    path("", views.report, name="report"),
    path('download-pm-report/', views.download_pm_report, name='download_pm_report'),
    path('download-jkk-report/', views.download_jkk_report, name='download_jkk_report'),
]