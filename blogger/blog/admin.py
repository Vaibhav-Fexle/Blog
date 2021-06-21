from django.contrib import admin
from .models import *

# Register your models here.

class BloggerAdmin(admin.ModelAdmin):
    list_display = ['__str__','user', 'is_staff', 'is_blogger', 'is_viewer']

admin.site.register(Blog)
admin.site.register(Categories)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Blogger, BloggerAdmin)