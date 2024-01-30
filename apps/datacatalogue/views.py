from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from core.decorators import restrict_user

mainPath = settings.MAINPATH

@login_required(login_url="/login/")
@restrict_user("dq_group")
def datacatalogue(request):
	return render(request, 'datacatalogue/datacatalogue.html', {})


@login_required(login_url="/login/")
@restrict_user("dq_group")
def initcatalogue(request):
	return render(request, 'datacatalogue/initcatalogue.html', {})


@login_required(login_url="/login/")
@restrict_user("dq_group")
def tempcatalogue(request):
	return render(request, 'datacatalogue/tempcatalogue.html', {})