from rest_framework.fields import ListField

from .models import *
from rest_framework import serializers


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = "__all__"
        many = True


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['title','description','categorie','pic1']
        # exclude = ['slug', 'comment_count', 'owner']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        many = True


class BloggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blogger
        # fields = "__all__"
        exclude = ['slug', 'user']
        many = True


class DataSerializer(serializers.Serializer):
    categoties = serializers.SerializerMethodField('get_categoties')
    blog = serializers.SerializerMethodField('get_blog')
    blogger = serializers.SerializerMethodField('get_blogger')

    def get_blogger(self):
        return BloggerSerializer(Blogger.objects.all(), many=True)
    def get_blog(self):
        return BlogSerializer(Blog.objects.all().order_by('-created')[4:14], many=True)
    def get_categoties(self):
        return CategoriesSerializer(Categories.objects.all(), many=True)
    class Meta:
        fields = ['categoties', 'blog', 'blogger']

