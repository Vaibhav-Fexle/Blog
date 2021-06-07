from collections import Counter

from django.shortcuts import render

from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, urls, views
from django.contrib.auth.decorators import login_required

from django.views import View

from .form import *
from .models import *
from .decorators import *
from taggit.models import Tag


# Create your views here.
def Popular():
    # test = Blog.objects.filter(id__in=t3).values('title').order_by()
    t1 = Comment.objects.all().order_by('-blog').values_list('blog', flat=True)
    t2 = Counter(t1)
    t3 = [ i for i,j in t2.most_common() ]
    popular = []
    for i in t3:
        popular.append(Blog.objects.filter(id=i)[0])
    return popular

def home(request,*args, **kagrs):
    return redirect("/home/")

class Home_View(View):
    template_name = 'index.html'
    queryset = Blog.objects.all()

    def get(self, request, *args, **kagrs):
        print('---home-GET---')
        blog_all = Blog.objects.all().order_by('-created')
        popular = Popular()
        recent = blog_all[0:4]
        blog = blog_all[4:14]
        categories = Categories.objects.all()
        content = {
            'popular': popular[0:4],
            'blog': blog,
            'blog_all': blog_all,
            'recent': recent,
            'cat': categories
        }
        return render(request, "index.html", content)


class Blog_View(View):

    def get(self, request,*args, **kagrs):
        print('---Blog-POST---')
        blog_all = Blog.objects.all().order_by('-created')
        recent = blog_all[0:3]
        blog = blog_all[3:8]
        categories = Categories.objects.all()
        content = {
            'blog': blog,
            'blog_all': blog_all,
            'new': recent,
            'cat': categories
        }
        return render(request, "blog.html", content)


class Category_View(View):
    def get(self, request, id=None, *args, **kagrs):
        print('---Category_View-GET---')
        if id != None:
            new_blogs = Blog.objects.filter(categorie__id=id).order_by('-created')
        else:
            new_blogs = Blog.objects.all().order_by('-created')
        popular = Popular()
        cat = Categories.objects.all()
        content = {
            'popular': popular[0:4],
            'new_blogs': new_blogs,
            'cat': cat
        }
        return render(request, "category.html", content)


class Detail_View(View):
    def get(self, request, id, *args, **kagrs):
        print('---Detail_View-GET---')
        blog_all = Blog.objects.all().order_by('-created')
        new = blog_all[0:3]
        cat = Categories.objects.all()
        blog = get_object_or_404(Blog, id=id)
        comment = Comment.objects.filter(blog=blog).order_by('-created')
        content = {
            'blog':blog,
            'commment':comment,
            'blog_all': new,
            'cat': cat
        }
        return render(request, "detail.html", content)

    def post(self, request, *args, **kagrs):
        print('---Detail_View-POST---')
        blog = get_object_or_404(Blog, id=kagrs['id'])
        if request.user.is_authenticated == True:
            fullname = request.user.first_name+request.user.last_name
            email = request.user.email
            owner = request.user
        else:
            fullname = request.POST.get('fullname')
            email = request.POST.get('email')
            owner = None
        description = request.POST.get('description')
        Comment.objects.create(blog=blog, owner=owner, fullname=fullname, email=email, description=description )
        return HttpResponseRedirect(request.path)


class User_Edit_View(View):
    def get(self, request, *args, **kagrs):
        print('---User_Edit_View-GET---')
        userr = request.user.blogger
        form = BloggerForm(instance=userr)
        content = {
            'form' : form
        }
        return render(request, "useredit.html", content)

    def post(self, request, *args, **kagrs):
        print('---User_Edit_View-POST---')
        userr = request.user.blogger
        form = BloggerForm(request.POST, request.FILES, instance=userr)
        if form.is_valid():
            form.save()
        return redirect("/user/")


class User_View(View):
    def get(get, request, id=None, *args, **kagrs):
        print('---User_View-GET---')
        if id != None:
            user = User.objects.filter(id=id)[0]
        else:
            user = request.user
        blog_all = Blog.objects.filter(owner=user)
        content = {
            'blog_all': blog_all,
            'user':user
        }
        return render(request, "user.html", content)


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
        content = {
            "form": form,
            }
        return render(request, "register.html", content)

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

