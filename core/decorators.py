from django.shortcuts import render
from django.core.exceptions import PermissionDenied
    
def restrict_user(*groups):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            if request.user.groups.filter(name__in=groups).exists():
                return function(request, *args, **kwargs)
            raise PermissionDenied()
        return wrapper
    return decorator