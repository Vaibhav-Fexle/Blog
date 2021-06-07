from django.contrib import admin
from django.urls import include,path

from .views import *

app_name='blog'
urlpatterns = [
    path('',Blog_View.as_view()),
    path('category/',Category_View.as_view()),
    path('category/<int:id>/',Category_View.as_view()),
    path('detail/',Detail_View.as_view()),
    path('detail/<int:id>/',Detail_View.as_view()),
]