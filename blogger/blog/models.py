from django.db import models
from django.contrib.auth.models import User
from django import forms
from django.template.defaultfilters import safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ckeditor.fields import *
from ckeditor_uploader.fields import *

# Create your models here.


class Categories(models.Model):
    title = models.CharField(max_length=50, unique=True )
    description = models.CharField(max_length=100)
    slug = models.SlugField(default=slugify(title))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)+slugify(self.id) # or self.slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    def len(self):
        return len(Blog.objects.filter(categorie=self))
    def urls(self):
        return f"/blog/category/{self.slug}/"

class Blog(models.Model):
    title = models.CharField(max_length=200)
    description_short = models.CharField(max_length=200)
    description = RichTextField()

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    photo = models.ImageField( default='noimage.jpg', upload_to='blog/' )
    categorie = models.ManyToManyField(Categories)
    created = models.DateTimeField(auto_now_add=True)

    comment_count = models.IntegerField(default=0)
    slug = models.SlugField(default=slugify(title))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)+slugify(self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    def short(self):
        return safe(self.description_short[0:100]) + '...'
    def comment(self):
        return Comment.objects.filter(blog=self).order_by('-created')
    def urls(self):
        return f"/blog/post/{self.slug}/"
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
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.blog) + str(self.owner) + str(self.description)

class Blogger(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_pic = models.ImageField(default='user/profil.png', upload_to='user/', )
    bio = models.TextField(blank=True, null=True, default="")
    joined = models.DateTimeField(auto_now_add=True)
    website = models.URLField(blank=True, null=True, default="", max_length=100)
    slug = models.SlugField(default=slugify(user))

    is_staff = models.BooleanField(default=False, help_text=_('Designates whether this user should be treated as site staff.'
                                                              'a staff user can add categories and update other user\'s status ') )
    is_blogger = models.BooleanField(default=False, help_text=_('Designates whether this user should be treated as blogger on site.'
                                                                'a blogger can create new blogs, view them and comment on them'))
    is_viewer = models.BooleanField(default=True, help_text=_('Designates whether this user should be treated as viewer site.'
                                                              'a viewer can view blogs and comment on it'))


    def save(self, *args, **kwargs):
        self.slug = slugify(self.user)      # or self.slug
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
