from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Blog)
admin.site.register(Categories)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Blogger)