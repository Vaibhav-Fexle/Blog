from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from taggit.models import Tag


# Create your models here.

class Categories(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def len(self):
        return len(Blog.objects.filter(categorie=self))
    def urls(self):
        return f"/blog/category/{self.id}/"


class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    pic1 = models.ImageField(null=True, blank=True, upload_to='blog/')
    pic2 = models.ImageField(null=True, blank=True, upload_to='blog/')
    # categorie = models.ForeignKey(Categories, null=True, on_delete=models.SET_NULL)
    categorie = models.ManyToManyField(Categories)
    created = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title
    def short(self):
        return self.description[0:140] + '...'
    def comment(self):
        return Comment.objects.filter(blog=self).order_by('-created')
    def urls(self):
        return f"/blog/detail/{self.id}/"
    def cat_1(self):
        cat_1 = [i for i in self.categorie.all()]
        return cat_1[0:1]
    def cat_2(self):
        cat_2 = [i for i in self.categorie.all()]
        return cat_2[0:2]


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    fullname = models.TextField(default='UNKNOWN', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.blog) + str(self.owner) + str(self.description)

    def reply(self):
        return Reply.objects.filter(replyed_to=self).order_by('-created')


class Reply(models.Model):
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    replyed_to = models.ForeignKey(Comment, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.owner) + str(self.description)


class Blogger(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    # DOB = models.DateField(null=True)
    user_pic = models.ImageField(default='user/profil.png', upload_to='user/', )
    bio = models.TextField(blank=True, null=True, default="")
    joined = models.DateTimeField(auto_now_add=True)
    website = models.CharField(blank=True, null=True, default="", max_length=100)
