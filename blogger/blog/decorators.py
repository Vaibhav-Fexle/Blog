from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from rest_framework import permissions

from rest_framework.authentication import *
from rest_framework.permissions import *

from .models import Blog


def unauth_user(view_fun):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('user_view')
        else:
            return view_fun(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = [i for i in request.user.groups.all().values_list('name',flat=True)]

            for i in allowed_roles:
                if i in group:
                    return view_func(request, *args, **kwargs)
            else:
                messages.info(request, 'You are not authorized to view this page')
                return redirect('home')

        return wrapper_func

    return decorator


def owner_user(view_fun):
    def wrapper_func(request, *args, **kwargs):
        if get_object_or_404(Blog, slug=kwargs.get('slug')).owner != request.user:
            messages.info(request, 'You can only Edit Blog which is created by you')
            return redirect('home')
        else:
            return view_fun(request, *args, **kwargs)

    return wrapper_func