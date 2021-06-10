from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from taggit.managers import TaggableManager
from taggit.models import Tag


# Create your models here.

class Categories(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    slug = models.SlugField(default=slugify(title))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title) # or self.slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    def len(self):
        return len(Blog.objects.filter(categorie=self))
    def urls(self):
        return f"/blog/category/{self.slug}/"


class Blog(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    pic1 = models.ImageField(null=True, blank=True, default='user/profil.png', upload_to='blog/')
    categorie = models.ManyToManyField(Categories)
    created = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    comment_count = models.IntegerField(default=0)
    slug = models.SlugField(default=slugify(title))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)+slugify(self.id) # or self.slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    def short(self):
        return self.description[0:140] + '...'
    def comment(self):
        return Comment.objects.filter(blog=self).order_by('-created')
    def urls(self):
        return f"/blog/detail/{self.slug}/"
    def cat_1(self):
        cat_1 = [i for i in self.categorie.all()]
        return cat_1[0:1]
    def cat_2(self):
        cat_2 = [i for i in self.categorie.all()]
        return cat_2[0:2]


    def count(self):
        self.comment_count = len(self.comment())
        self.save()
        return len(self.comment())


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.blog) + str(self.owner) + str(self.description)

    def reply(self):
        return Reply.objects.filter(replyed_to=self).order_by('-created')


class Reply(models.Model):                                                  # no need
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
    website = models.URLField(blank=True, null=True, default="", max_length=100)
    slug = models.SlugField(default=slugify(user))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.user) # or self.slug
        super().save(*args, **kwargs)
