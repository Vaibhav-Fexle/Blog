
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import *


class LoginForm( forms.Form ):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Firstname"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))

class RegisterForm( UserCreationForm ):
    username    = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "username"}))
    email       = forms.EmailField()

    class Meta:
        model = User
        fields=['username','email','password1','password2']

class BloggerForm(forms.ModelForm):
    class Meta:
        model = Blogger
        fields = '__all__'
        exclude = ['user']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        # exclude = ['owner','blog']
