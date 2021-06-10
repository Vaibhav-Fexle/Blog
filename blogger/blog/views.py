from collections import Counter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.shortcuts import render

from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, urls, views
from django.contrib.auth.decorators import login_required

# from django.views import View
from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import FormMixin, CreateView, ModelFormMixin

from .form import *
from .models import *
from .decorators import *
from taggit.models import Tag

from .serializers import *

# Create your views here.
# def popular():
    # [ i.count() for i in Blog.objects.all() ]
    # test = Blog.objects.all().order_by('-comment_count')
    #
    # test = Blogger.objects.all()
    # for i in test:
    #     i.save()

def home(request,*args, **kagrs):
    return redirect("/home/")

data_all = DataSerializer(data={'categories':Categories.objects.all(),
                                'popular': Blog.objects.all().order_by('-comment_count')[0:3],
                                'blog': Blog.objects.all().order_by('-created')[4:14],
                                'recent': Blog.objects.all().order_by('-created')[0:4],
                            })
data_all.is_valid(raise_exception=True)

class Home_View(View):
    template_name = 'index.html'
    queryset = Blog.objects.all().order_by('-created')

    def get(self, request, *args, **kagrs):
        return render(request, self.template_name, data_all.initial_data)


class Blog_View(ListView):
    paginator_class = Paginator
    paginate_by = 2
    model = Blog
    template_name = "blog.html"
    queryset = Blog.objects.all().order_by('-created')

    def get_queryset(self):
        if self.request.GET.get('search') != None:
            search = self.request.GET.get('search')
            return Blog.objects.filter(title=search).order_by('-created')
        else:
            return Blog.objects.all().order_by('-created')


    def get(self, request,*args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)

        data = data_all.initial_data
        data.update({'blog_all': page_obj, 'pages': int(self.paginator_class.num_pages) })

        return render(request, self.template_name, data)


class Blog_Create_View(LoginRequiredMixin, View, ModelFormMixin):
    login_url = '/login/'
    redirect_field_name = 'User'
    template_name = "blog_create.html"

    model = Blog
    form_class = BlogForm

    def get(self, request,*args, **kagrs):
        data = data_all.initial_data
        data.update({'form' : self.get_form_class() })
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        self.user = request.user
        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
        else:
            self.form_invalid(form, request)
        return redirect("/user/")

    def form_valid(self, form):
        data = form.cleaned_data
        blog = Blog.objects.create(owner=self.user, title=data['title'], description=data['description'], pic1=data['pic1'])
        blog.categorie.set(data['categorie'])
        return redirect("/user/")

    def form_invalid(self, form, *args, **kwargs):
        return HttpResponseRedirect(form)


class Category_View(View):
    template_name = "category.html"
    paginator_class = Paginator
    paginate_by = 2

    def get_queryset(self, slug=None, *args, **kagrs):
        if slug != None:
            return Blog.objects.filter(categorie__slug=slug).order_by('-created')
        else:
            return Blog.objects.all().order_by('-created')

    def get(self, request, slug=None, *args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(slug), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)

        data = data_all.initial_data
        data.update({'blog_all': page_obj,'pages': int(self.paginator_class.num_pages) })

        return render(request, self.template_name, data)


class Detail_View(DetailView):
    template_name = "detail.html"
    model = Blog

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get_queryset(self):
        return Comment.objects.filter(blog=self.get_object().id).order_by('-created')

    def get(self, request, slug=None, *args, **kagrs):

        data = data_all.initial_data
        data.update({'blog_obj': self.get_object(),
                     'commment': self.get_queryset()
                     })

        return render(request, self.template_name, data)

    @method_decorator(login_required)
    def post(self, request, *args, **kagrs):
        blog = self.get_object()
        owner = None
        if request.user.is_authenticated == True:
            owner = request.user
        description = request.POST.get('description')
        Comment.objects.create(blog=blog, owner=owner,description=description )
        blog.count()
        return HttpResponseRedirect(request.path)


class User_Edit_View(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'User'

    template_name = "useredit.html"

    def get_user(self):
        return self.request.user.blogger

    def get(self, request, *args, **kagrs):
        form = BloggerForm(instance=self.get_user())

        data = data_all.initial_data
        data.update({'form' : form, })

        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        form = BloggerForm(request.POST, request.FILES, instance=self.get_user())
        if form.is_valid():
            form.save()
        else:
            data = data_all.initial_data
            data.update({'form': form, })
            return render(request, self.template_name, data)
        return redirect("/user/")


class User_View(LoginRequiredMixin, DetailView ):
    template_name = "user.html"
    login_url = '/login/'
    redirect_field_name = 'User'
    model = Blogger

    def get_slug_field(self):
        return self.kwargs.get('slug') or self.request.user.blogger.slug

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()).user \
               or self.request.user

    def get_queryset(self):
        return Blog.objects.filter(owner=self.get_object())

    def get(self, request, *args, **kagrs):
        data = data_all.initial_data
        data.update({'user': self.get_object(),
                     'blog_all': self.get_queryset() })

        return render(request, self.template_name, data)


#TODO       LOGIN - LOGOUT - REGISTER

# def login_view(request,*args, **kagrs):
#     form = LoginForm()
#     if request.method == "POST":
#         un = request.POST.get("username")
#         pw = request.POST.get("password1")
#         user = authenticate(request, username=un, password=pw)
#         print(user,un,pw)
#         if user is not None:
#             login(request, user)
#             return redirect('/home/')
#     content = {
#         "form": form,
#     }
#     return render(request, "login.html", content)

class Register_View(View):
    def get(self, request,*args, **kagrs):
        form = RegisterForm()
        return render(request, "register.html", { "form": form })

    def post(self, request, *args, **kagrs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            Blogger.objects.create(user=user)
            login(request, user)
            return redirect("/user/")

# def logoutuser(request , *args , **kagrs):
#     logout(request)
#     return redirect("/login/")



#TODO REMOVED

def about_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content={
        'blog'  :   blog
    }
    return render(request,"about.html", content )

def contact_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content={
        'blog'  :   blog
    }
    return render(request,"contact.html", content )

'''

[
    {
        "model": "blog.blog", 
        "pk": 9, "fields": {
                            "title": "asd", 
                            "description": "", 
                            "owner": 2, 
                            "pic1": "user/profil.png", 
                            "created": "2021-06-08T05:27:27.910Z", 
                            "comment_count": 0, 
                            "slug": "asd", 
                            "categorie": [1, 2]
                            }
    }, 
    {"model": "blog.blog", "pk": 8, "fields": {"title": "asdasd", "description": "asdasdasd", "owner": 2, "pic1": "blog/640x480-bazaar-solid-color-background.jp
g", "created": "2021-06-08T05:23:41.099Z", "comment_count": 0, "slug": "asdasd", "categorie": [1, 2]}}, {"model": "blog.blog", "pk": 7, "fields": {"title": "asdasd", "description": "asdasd
asdasd", "owner": 1, "pic1": "blog/640x480-air-force-dark-blue-solid-color-background.jpg", "created": "2021-06-08T05:22:47.442Z", "comment_count": 0, "slug": "asdasd", "categorie": [3]}},
 {"model": "blog.blog", "pk": 6, "fields": {"title": "asd", "description": "", "owner": 1, "pic1": "user/profil.png", "created": "2021-06-08T04:35:53.198Z", "comment_count": 0, "slug": "as
d", "categorie": [1]}}, {"model": "blog.blog", "pk": 5, "fields": {"title": "asd", "description": "asdasd", "owner": 1, "pic1": "blog/640x480-alabama-crimson-solid-color-background_sJySThS
.jpg", "created": "2021-06-08T04:21:56.198Z", "comment_count": 0, "slug": "asd", "categorie": [1]}}, {"model": "blog.blog", "pk": 1, "fields": {"title": "testblog1", "description": "testbl
og1", "owner": 1, "pic1": "blog/640x480-alabama-crimson-solid-color-background.jpg", "created": "2021-06-07T13:33:35.623Z", "comment_count": 2, "slug": "testblog1", "categorie": [1]}}]


'''