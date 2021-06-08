
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError

from .models import *


# class LoginForm( AuthenticationForm ):
#     username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Firstname"}))
#     password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))

# class LoginForm( AuthenticationForm ):
#     def confirm_login_allowed(self, user):
#         if not user.is_active:
#             raise ValidationError(
#                 _("This account is inactive."),
#                 code='inactive')
#
#         if user.username.startswith('b'):
#             raise ValidationError(
#                 _("Sorry, accounts starting with 'b' aren't welcome here."),
#                 code='no_b_users',
#             )
#
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
        exclude = ['user','slug']

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = '__all__'
        exclude = ['slug','comment_count','owner', 'tags']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = '__all__'
        # exclude = ['owner','blog']
