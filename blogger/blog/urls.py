from django.contrib import admin
from django.urls import include,path

from .views import *

app_name='blog'
urlpatterns = [
    path('',Blog_View.as_view(), name='blog'),

    path('category/',Category_View.as_view(), name='category_view'),
    path('category/create/',Category_Create_View.as_view(), name='category_create_view'),
    path('category/<slug:slug>/',Category_View.as_view(),  name='category_single_view'),
    path('category/<slug:slug>/delete/',Category_Delete_View.as_view(),  name='category_delete_view'),

    path('create/',Blog_Create_View.as_view(),  name='blog_create_view'),
    path('post/<slug:slug>/',Blog_Detail_View.as_view(),  name='blog_detail_view'),
    path('post/<slug:slug>/edit/',Blog_Edit_View.as_view(),  name='blog_edit_view'),
    path('post/<slug:slug>/delete/',Blog_Delete_View.as_view(),  name='blog_delete_view'),


]