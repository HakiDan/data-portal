from django.shortcuts import render, HttpResponse
from apps.upload.views import *
from django.contrib.auth.decorators import login_required

@login_required(login_url="/login/")
@restrict_user("dq_group")
def dataupdate(request):
    return render(request, 'datacleaning/dataupdate.html')
