from django.contrib import admin
from .models import *

# Register your models here.

class BloggerAdmin(admin.ModelAdmin):
    list_display = ['__str__','user', 'is_staff', 'is_blogger', 'is_viewer','joined']

class BlogAdmin(admin.ModelAdmin):
    list_display = ['__str__','owner', 'created', 'comment_count']

class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['__str__']

class CommentAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'blog', 'owner']

admin.site.register(Blog, BlogAdmin)
admin.site.register(Categories, CategoriesAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Blogger, BloggerAdmin)