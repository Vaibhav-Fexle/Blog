from rest_framework.fields import ListField

from .models import *
from rest_framework import serializers

class CategoriesSerializer(serializers.Serializer):
    class Meta:
        model = Categories
        field = "__all__"
        many = True

class BlogSerializer(serializers.Serializer):
    class Meta:
        model = Blog
        field = "__all__"
        many = True

class CommentSerializer(serializers.Serializer):
    class Meta:
        model = Comment
        field = "__all__"
        many = True


class BloggerSerializer(serializers.Serializer):
    class Meta:
        model = Blogger
        field = "__all__"
        many = True

class DataSerializer(serializers.Serializer):
    categoties = CategoriesSerializer(required=False, many=True)
    blog = ListField(BlogSerializer(required=False, many=True))
    comments = CommentSerializer(required=False, many=True)
    blogger = BloggerSerializer(required=False, many=True)

    class Meta:
        model = Categories, Blog, Comment, Blogger
        field=['categories', 'blog', 'comments', 'blogger' ]
        many = True
