from django.shortcuts import redirect
from rest_framework import permissions

from rest_framework.authentication import *
from rest_framework.permissions import *

def unauth_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/home/')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print('--')
        return obj.owner == request.user