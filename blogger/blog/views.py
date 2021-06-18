
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import login, views
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django.utils.decorators import method_decorator
from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import DeleteView

from .decorators import *
from .serializers import *


def home(request,*args, **kagrs):
    return redirect("/home/")

def get_data_one():
    data = {'categories' : CategoriesSerializer(Categories.objects.all(), many=True).instance}
    return data

def get_data():
    blog = Blog.objects.all()
    data = {
        'categories' : CategoriesSerializer(Categories.objects.all(), many=True).instance,
        'popular' : BlogSerializer( blog.order_by('-comment_count')[0:6], many=True).instance,
        'blog' : BlogSerializer( blog.order_by('-created')[5:15] ,many=True).instance,
        'recent': BlogSerializer( blog.order_by('-created')[0:4], many=True).instance,
       }
    return data


class Home_View(View):
    template_name = 'index.html'
    queryset = Blog.objects.all().order_by('-created')

    def get(self, request, *args, **kagrs):
        return render(request, self.template_name, get_data())


class Blog_View(ListView):
    paginator_class = Paginator
    paginate_by = 6
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

        data = get_data()
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
        data = get_data()
        data['form'] = BlogSerializer()

        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('create_blog') == 'cancel':
            return HttpResponseRedirect('../')

        self.user = request.user
        form = BlogSerializer(data=request.POST)
        if form.is_valid():
            self.post_valid(form.data)
        else:
            data = get_data()
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
        data = get_data()
        data['form'] = BlogSerializer(instance=self.get_object())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('update_blog') == 'cancel':
            return HttpResponseRedirect('../')

        form = BlogSerializer(instance=self.get_object(), data=request.POST, partial=True)
        if form.is_valid():
            blog = form.save()
            if request.FILES.get('pic1'):
                blog.pic1 = request.FILES.get('pic1')
            blog.save()
        else:
            data = get_data()
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
        return render(request, self.template_name, {'blog_obj':self.get_object()})

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete') == 'delete':
            obj = self.get_object()
            obj.delete()
            return redirect(self.success_url)
        return HttpResponseRedirect('../')


class Category_View(View):
    template_name = "category.html"
    paginator_class = Paginator
    paginate_by = 6

    def get_queryset(self, slug=None, *args, **kagrs):
        if slug != None:
            return Blog.objects.filter(categorie__slug=slug).order_by('-created')
        else:
            return Blog.objects.all().order_by('-created')

    def get(self, request, slug=None, *args, **kagrs):
        self.paginator_class = self.paginator_class(self.get_queryset(slug), self.paginate_by)
        page_number = request.GET.get('page')
        page_obj = self.paginator_class.get_page(page_number)

        data = get_data()
        data['blog_objs'] = page_obj
        data['slug'] = slug
        data['pages'] = int(self.paginator_class.num_pages)

        return render(request, self.template_name, data)

class Category_Create_View(View, LoginRequiredMixin):
    template_name = "categorycreate.html"
    def get(self, request, slug=None, *args, **kagrs):
        data = get_data()
        data['form'] = CategoriesSerializer()
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('create') == 'cancel':
            return HttpResponseRedirect('../')

        form = CategoriesSerializer(data=request.POST)
        if form.is_valid():
            form.save()
        else:
            data = get_data_one()
            data['form'] = form
            return render(request, self.template_name, data)

        return redirect('blog:category_view')

class Category_Delete_View(DeleteView, LoginRequiredMixin):
    login_url = '/login/'
    template_name = "categorydelete.html"
    success_url = '/blog/category/'
    model = Categories

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get(self, request, *args,**kwargs):
        return render(request, self.template_name, {'obj':self.get_object()})

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete') == 'delete':
            obj = self.get_object()
            obj.delete()
            return redirect(self.success_url)
        return HttpResponseRedirect('../')


class Detail_View(DetailView):
    template_name = "detail.html"
    model = Blog

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    def get(self, request, *args, **kagrs):
        data = get_data()
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
        data = get_data()
        data['form'] = BloggerSerializer(instance=self.get_user())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('update') == 'cancel':
            return HttpResponseRedirect('../')

        form = BloggerSerializer(instance=self.get_user(), data=request.POST, partial=True)
        if form.is_valid():
            user = form.save()
            if request.FILES.get('user_pic'):
                user.user_pic = request.FILES.get('user_pic')
            user.save()
        else:
            data = get_data()
            data['form'] = form
            return render(request, self.template_name, data)
        return redirect("/user/")

class User_Update_View(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = "userupdate.html"

    def get_user(self):
        self.slug = self.kwargs.get('slug')
        return get_object_or_404(Blogger, slug=self.slug) or self.request.user.blogger

    def get(self, request, *args, **kwargs):
        data = get_data()
        data['form'] = BloggerUpdateSerializer(instance=self.get_user())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        if request.POST.get('update') == 'cancel':
            return HttpResponseRedirect('/user/{}/'.format(self.kwargs.get('slug')))

        form = BloggerUpdateSerializer(instance=self.get_user(), data=request.POST )
        if form.is_valid():
            form.save()
        else:
            data = get_data()
            data['form'] = form
            return render(request, self.template_name, data)
        return redirect("/user/{}/".format(self.slug))

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

        data = get_data()
        data['blog_objs'] = page_obj
        data['pages'] = int(self.paginator_class.num_pages)
        data['user'] = self.get_object()

        return render(request, self.template_name, data)


class Register_View(View):
    template_name = "register.html"

    def get(self, request,*args, **kagrs):
        form = RegisterSerializer()
        data = get_data()
        data['form'] = form
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('register') == 'cancel':
            return HttpResponseRedirect('/home/')

        print(request.POST)
        form = RegisterSerializer(data=request.POST)
        if form.is_valid():
            user = form.save()
            blogger = Blogger.objects.create(user=user)
            blogger.save()
            login(request, user)
            return redirect("/user/")
        else:
            data = get_data()
            data['form'] = form
            return render(request, self.template_name, data)

class Login_View(views.LoginView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoriesSerializer(Categories.objects.all(), many=True).instance
        return context



def about_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content = { 'blog'  :   blog }
    return render(request,"about.html", content )

def contact_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content = { 'blog'  :   blog }
    return render(request,"contact.html", content )
