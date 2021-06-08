from django.contrib import admin
from django.urls import include,path

from .views import *

app_name='blog'
urlpatterns = [
    path('',Blog_View.as_view(), name='blog'),
    path('category/',Category_View.as_view(), name='category_view'),
    path('category/<slug:slug>/',Category_View.as_view(),  name='category_single_view'),
    # path('detail/<int:id>/',Detail_View.as_view(),  name='detail_view'),
    path('detail/<slug:slug>/',Detail_View.as_view(),  name='detail_view'),
    path('create/',Blog_Create_View.as_view(),  name='blog_create_view'),
]