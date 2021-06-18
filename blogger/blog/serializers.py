from .models import *
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password




class CategoriesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True,
                                    validators=[UniqueValidator(queryset=Categories.objects.all())])
    class Meta:
        model = Categories
        exclude = ['slug']


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['title','description','categorie','photo']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        many = True


class BloggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blogger
        exclude = ['slug', 'user', 'is_staff', 'is_blogger', 'is_viewer']


class BloggerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blogger
        fields = ['is_staff', 'is_blogger']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
                                    required=True,
                                    validators=[UniqueValidator(queryset=User.objects.all())]
                                )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password],
                                     style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']
        extra_kwargs = {
                        'first_name': {'required': True},
                        'last_name': {'required': True}
                    }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
                                    username=validated_data['username'],
                                    email=validated_data['email'],
                                    first_name=validated_data['first_name'],
                                    last_name=validated_data['last_name']
                                )
        user.set_password(validated_data['password'])
        user.save()

        return user

