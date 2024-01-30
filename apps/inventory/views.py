from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from core.decorators import restrict_user

@login_required(login_url="/login/")
@restrict_user("dq_group")
def inventory(request):
	return render(request, 'inventory/inventorymanagement.html', {})

def add(request):
	return render(request, 'inventory/additem.html', {})

def edit(request):
	return render(request, 'inventory/edititem.html', {})