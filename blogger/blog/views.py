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
from django.views.generic.edit import FormMixin, CreateView, ModelFormMixin, DeletionMixin, DeleteView

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

data = {
        'categories' : CategoriesSerializer(Categories.objects.all(), many=True).instance,
        'popular' : BlogSerializer(Blog.objects.all().order_by('-comment_count')[0:4], many=True).instance,
        'blog' : BlogSerializer(Blog.objects.all().order_by('-created')[5:15] ,many=True).instance,
        'recent': BlogSerializer(Blog.objects.all().order_by('-created')[0:4], many=True).instance,
       }


class Home_View(View):
    template_name = 'index.html'
    queryset = Blog.objects.all().order_by('-created')

    def get(self, request, *args, **kagrs):
        return render(request, self.template_name, data)


class Blog_View(ListView):
    paginator_class = Paginator
    paginate_by = 3
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

        data['blog_objs'] = page_obj
        data['pages'] = int(self.paginator_class.num_pages)

        return render(request, self.template_name, data)


class Blog_Create_View(LoginRequiredMixin, View ):
    login_url = '/login/'
    redirect_field_name = 'User'
    template_name = "blog_create.html"
    model = Blog

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get(self, request,*args, **kwargs):
        data['form'] = BlogSerializer()

        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        self.user = request.user
        form = BlogSerializer(data=request.POST)
        if form.is_valid():
            self.post_valid(form.data)
        else:
            data['form'] = form
            return render(self.request, self.template_name, data)
        return redirect("/user/")


    def post_valid(self, data ):
        blog = Blog.objects.create( owner=self.user,
                                    title=data['title'],
                                    description=data['description']
                                  )
        if self.request.FILES.get('pic1'):
            blog.pic1 = self.request.FILES.get('pic1')
        blog.categorie.set(data['categorie'])
        blog.save()
        return redirect("/user/")


class Blog_Update_View(LoginRequiredMixin, View ):
    login_url = '/login/'
    template_name = "blog_create.html"
    model = Blog

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get(self, request,*args, **kwargs):
        data['form'] = BlogSerializer(instance=self.get_object())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        form = BlogSerializer(instance=self.get_object(), data=request.POST, partial=True)
        if form.is_valid():
            blog = form.save()
            if request.FILES.get('pic1'):
                blog.pic1 = request.FILES.get('pic1')
            blog.save()
        else:
            data['form'] = form
            return render(self.request, self.template_name, data)

        return HttpResponseRedirect('/blog/post/{}/'.format(blog.slug))


class Blog_Delete_View(DeleteView, LoginRequiredMixin):
    login_url = '/login/'
    template_name = "blog_delete.html"
    model = Blog
    success_url = '/user/'

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get(self, request, *args,**kwargs):
        return render(self.request, self.template_name, {'blog_obj':self.get_object()})


class Category_View(View):
    template_name = "category.html"
    paginator_class = Paginator
    paginate_by = 3

    def get_queryset(self, slug=None, *args, **kagrs):
        if slug != None:
            return Blog.objects.filter(categorie__slug=slug).order_by('-created')
        else:
            return Blog.objects.all().order_by('-created')

    def get(self, request, slug=None, *args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(slug), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)

        data['blog_objs'] = page_obj
        data['pages'] = int(self.paginator_class.num_pages)

        return render(request, self.template_name, data)


class Detail_View(DetailView):
    template_name = "detail.html"
    model = Blog

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get(self, request, *args, **kagrs):
        data['blog_obj'] = self.get_object()

        return render(request, self.template_name, data)

    @method_decorator(login_required)
    def post(self, request, *args, **kagrs):
        blog = self.get_object()
        owner = request.user or None
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
        data['form'] = BloggerSerializer(instance=self.get_user())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        form = BloggerSerializer(instance=self.get_user(), data=request.POST, partial=True)
        if form.is_valid():
            user = form.save()
            if request.FILES.get('user_pic'):
                user.user_pic = request.FILES.get('user_pic')
            user.save()
        else:
            data['form'] = form
            return render(request, self.template_name, data)
        return redirect("/user/")


class User_View(LoginRequiredMixin, DetailView ):
    template_name = "user.html"
    login_url = '/login/'
    redirect_field_name = 'User'
    model = Blogger

    paginator_class = Paginator
    paginate_by = 4

    def get_slug_field(self):
        return self.kwargs.get('slug') or self.request.user.blogger.slug

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()).user \
               or self.request.user

    def get_queryset(self):
        return Blog.objects.filter(owner=self.get_object()).order_by('-created')

    def get(self, request, *args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)

        data['blog_objs'] = page_obj
        data['pages'] = int(self.paginator_class.num_pages)
        data['user'] = self.get_object()

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

#TODO same userame check
class Register_View(View):
    def get(self, request,*args, **kagrs):
        form = RegisterForm()
        return render(request, "register.html", { "form": form })

    def post(self, request, *args, **kagrs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = form.save()
            blogger = Blogger.objects.create(user=user)
            blogger.save()
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
