from django.contrib import admin
from django.urls import include,path

from .views import *

app_name='blog'
urlpatterns = [
    path('',blog_view),
    path('category/',category_view),
    path('category/<int:id>/',category_view),
    path('detail/',detail_view),
    path('detail/<int:id>/',detail_view),
]