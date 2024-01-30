# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path("Xlh7K35!tp0/", admin.site.urls),          # Django admin route
    path("", include("apps.authentication.urls")), # Auth routes - login / register
    path("", include("apps.home.urls")),           # UI Kits Html files
    path("history/", include("apps.history.urls")),
    path("upload/", include("apps.upload.urls")),    
    path("data-cleaning/", include("apps.datacleaning.urls")),  
    path("masterlist-budget/", include("apps.masterlist.urls")), # link for apps function not html page.... multiple html page can be under a template folder
    path("masterlist-nec/", include("apps.masterlistnec.urls")), # link for apps function not html page.... multiple html page can be under a template folder
    path("soalan-lazim/", include("apps.faq.urls")),
    path("report/", include('apps.report.urls')),
    path("validation/", include('apps.validation.urls')),
    path("data-catalogue/", include('apps.datacatalogue.urls')),
    path("inventory/", include('apps.inventory.urls')),
    path("validation/", include('apps.validation.urls')),
]

handler404 = "core.error.page_not_found"
handler500 = "core.error.server_error"
handler403 = "core.error.permission_denied"
