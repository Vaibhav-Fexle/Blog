"""blogger URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin, auth
from django.urls import include,path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import urls, views
from blog.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),



    path('user/', User_View.as_view(), name='user_view'),
    path('user/<int:id>/', User_View.as_view(), name='user_view'),
    path('user/edit/', User_Edit_View.as_view(), name='user_edit_view'),


    path('blog/', include('blog.urls')),

    # path('home/',home, name='home'),
    path('home/',Home_View.as_view(), name='home_view'),

    path('about/',about_view,name='about_view'),
    path('contact/',contact_view,name='contact_view'),



    # path('login/', login_view, name='login_view'),
    # path('logout/', logoutuser, name="logout"),
    path('login/', auth.views.LoginView.as_view(template_name='login.html'),
                                                name='login_view'),
    path('logout/', auth.views.LogoutView.as_view(), name="logout"),

    path('register/', Register_View.as_view(), name='register_view'),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
