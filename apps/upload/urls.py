from django.urls import path
from apps.upload import views
from . import views
from apps.upload.views import FileUploadView

urlpatterns = [
    path("", FileUploadView.as_view(), name="upload"),
    path('check-column/', views.checkColumn, name='check-column'),
    path('check-data-submission/<str:initiative>/<str:file_name>/<str:template_name>/<str:file_ext>/<str:sub_init_id>/', 
         views.dataValidation_submission, name='datavalidation_submission'),
    path('replace-header/', views.replaceHeader, name='replaceHeader'),
    path('cancel-submission/', views.cancel_submission, name='cancel_submission'),
    path('dq-lvl-one/', views.dq_lvl_one, name='dq_lvl_one'),
    path('download-file-accepted/', views.download_file_accepted, name='download_file_accepted'),
    path('download-file-rejected/', views.download_file_rejected, name='download_file_rejected'),
]
