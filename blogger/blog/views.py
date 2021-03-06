from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth import login, views, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import View, ListView, DetailView
from django.views.generic.edit import DeleteView, CreateView, UpdateView

from .decorators import *
from .form import BlogForm
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
        'recent': BlogSerializer( blog.order_by('-created')[0:6], many=True).instance,
       }
    return data


class Home_View(View):
    template_name = 'index.html'
    queryset = Blog.objects.all().order_by('-created')

    def get(self, request, *args, **kagrs):
        return render(request, self.template_name, get_data())


class Blog_View(ListView):
    paginator_class = Paginator
    paginate_by = 10
    model = Blog
    template_name = "blog.html"
    queryset = Blog.objects.all().order_by('-created')

    def get_queryset(self):
        if self.request.GET.get('search') != None:
            search = self.request.GET.get('search')
            messages.info(self.request, f'Searching: {search}')
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

class Blog_Detail_View(DetailView):
    template_name = "blog_detail.html"
    model = Blog
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        messages.info(request, 'New Comment added on Blog')
        return HttpResponseRedirect(request.path)

class Blog_Create_View(LoginRequiredMixin, CreateView ):
    login_url = '/login/'
    redirect_field_name = 'User'
    template_name = "blog_create.html"
    model = Blog
    permission_classes = [IsAuthenticated]

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    @method_decorator(allowed_users(['blogger']))
    def get(self, request,*args, **kwargs):
        data = get_data()
        data['form'] = BlogSerializer()
        data['description'] = BlogForm()

        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('create_blog') == 'cancel':
            return HttpResponseRedirect('../')

        self.user = request.user
        form = BlogSerializer(data=request.POST)
        form.description = request.POST.get('description')
        form2 = BlogForm(request.POST)
        data = get_data()
        if form.is_valid():
            if not form2.is_valid():
                data['form'] = form
                data['description'] = form2
                return render(self.request, self.template_name, data)
            self.post_valid(form.data)
        else:
            data['description'] = form2
            data['form'] = form
            return render(self.request, self.template_name, data)
        return redirect("/user/")

    def post_valid(self, data ):
        blog = Blog.objects.create( owner=self.user,
                                    title=data['title'],
                                    description=self.request.POST.get('description')
                                  )
        if self.request.FILES.get('photo'):
            blog.photo = self.request.FILES.get('photo')
        blog.categorie.set(data['categorie'])
        blog.save()
        messages.info(self.request, f'New Blog Added: {blog.title}')
        return redirect("/user/")

class Blog_Edit_View(LoginRequiredMixin, UpdateView ):
    login_url = '/login/'
    template_name = "blog_create.html"
    model = Blog
    permission_classes = [IsAuthenticated]

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    @method_decorator(allowed_users(['blogger']))
    @method_decorator(owner_user)
    def get(self, request,*args, **kwargs):
        data = get_data()
        data['form'] = BlogSerializer(instance=self.get_object())
        data['description'] = BlogForm(instance=self.get_object())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('update_blog') == 'cancel':
            return HttpResponseRedirect('../')

        form = BlogSerializer(instance=self.get_object(), data=request.POST, partial=True)
        if form.is_valid():
            blog = form.save()
            if request.FILES.get('photo'):
                blog.photo = request.FILES.get('photo')
            blog.description = self.request.POST.get('description')
            blog.save()
            messages.info(request, f'Blog Updated: {blog.title}')
        else:
            data = get_data()
            data['form'] = form
            data['description'] = BlogForm(instance=self.get_object())
            return render(self.request, self.template_name, data)

        return HttpResponseRedirect('/blog/post/{}/'.format(blog.slug))

class Blog_Delete_View(DeleteView, LoginRequiredMixin):
    login_url = '/login/'
    template_name = "blog_delete.html"
    model = Blog
    success_url = '/user/'
    permission_classes = [IsAuthenticated]

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    @method_decorator(allowed_users(['blogger']))
    def get(self, request, *args,**kwargs):
        return render(request, self.template_name, {'blog_obj':self.get_object()})

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete') == 'delete':
            obj = self.get_object()
            blog = obj.title
            obj.delete()
            messages.info(request, f'Blog Deleted: {blog}')
            return redirect(self.success_url)
        return HttpResponseRedirect('../')


class Category_View(View):
    template_name = "category.html"
    paginator_class = Paginator
    paginate_by = 10

    def get_queryset(self, slug=None, *args, **kagrs):
        if slug != None:
            messages.info(self.request, f'{Categories.objects.filter(slug=slug)[0]} Categorie')
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
    permission_classes = [IsAuthenticated]

    @method_decorator(allowed_users(['staff']))
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
            messages.info(request, 'Categorie Added')
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
    permission_classes = [IsAuthenticated]

    def get_slug_field(self):
        return self.kwargs.get('slug') or None

    def get_object(self):
        return get_object_or_404(self.model, slug=self.get_slug_field()) or None

    @method_decorator(allowed_users(['staff']))
    def get(self, request, *args,**kwargs):
        return render(request, self.template_name, {'obj':self.get_object()})

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete') == 'delete':
            obj = self.get_object()
            obj.delete()
            messages.info(request, 'Categorie Deleted')
            return redirect(self.success_url)

        return HttpResponseRedirect('../')


class User_View(LoginRequiredMixin, DetailView ):
    template_name = "user.html"
    login_url = '/login/'
    redirect_field_name = 'User'
    model = Blogger

    paginator_class = Paginator
    paginate_by = 8

    permission_classes = [IsAuthenticatedOrReadOnly]

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

class User_Edit_View(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'User'
    template_name = "useredit.html"
    permission_classes = [IsAuthenticated]

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
        data = get_data()
        if form.is_valid():
            user = form.save()
            if request.FILES.get('user_pic'):
                user.user_pic = request.FILES.get('user_pic')
            user.save()
            messages.info(request,'User Profile Updated')
        else:
            data['form'] = form
            return render(request, self.template_name, data)
        return redirect("/user/")

class User_Update_View(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = "userupdate.html"
    permission_classes = [IsAuthenticated]

    def get_user(self):
        self.slug = self.kwargs.get('slug')
        return get_object_or_404(Blogger, slug=self.slug) or self.request.user.blogger

    @method_decorator(allowed_users(['staff']))
    def get(self, request, *args, **kwargs):
        data = get_data()
        data['form'] = BloggerUpdateSerializer(instance=self.get_user())
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        if request.POST.get('update') == 'cancel':
            return HttpResponseRedirect('/user/{}/'.format(self.kwargs.get('slug')))

        form = BloggerUpdateSerializer(instance=self.get_user(), data=request.POST )
        if form.is_valid():
            user = form.save()
            if user.is_staff:
                user.user.groups.add(3)
                user.user.is_staff = True
                user.save()
            else:
                user.user.groups.remove(3)
                user.user.is_staff = False
                user.save()

            if user.is_blogger:
                user.user.groups.add(2)
                user.save()
            else:
                user.user.groups.remove(2)
                user.save()

            messages.info(request, 'User Updated')
        else:
            data = get_data()
            data['form'] = form
            return render(request, self.template_name, data)
        return redirect("/user/{}/".format(self.slug))


class Register_View(View):
    template_name = "register.html"

    @method_decorator(unauth_user)
    def get(self, request,*args, **kagrs):
        form = RegisterSerializer()
        data = get_data()
        data['form'] = form
        return render(request, self.template_name, data)

    def post(self, request, *args, **kagrs):
        if request.POST.get('register') == 'cancel':
            return HttpResponseRedirect('/home/')

        form = RegisterSerializer(data=request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add('viewer')
            blogger = Blogger.objects.create(user=user)
            blogger.save()
            login(request, user)
            messages.info(request, f'Thanks For Joing {blogger}')
            return redirect("/user/")
        else:
            data = get_data()
            data['form'] = form
            return render(request, self.template_name, data)

class Login_View(views.LoginView):
    template_name = 'login.html'
    # permission_classes = [IsAuthenticated]

    @method_decorator(unauth_user)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoriesSerializer(Categories.objects.all(), many=True).instance
        return context

    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.info(self.request,f'Welcome back {form.get_user()}')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        a = form.errors.get('__all__')
        messages.info(self.request, f'{a}')
        return HttpResponseRedirect(self.request.path)

class Logout_View(views.LogoutView):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        messages.info(self.request, f'successfully Logout : {user}')
        next_page = self.get_next_page()
        if next_page:
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)


def about_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content = { 'blog'  :   blog }
    return render(request,"about.html", content )

def contact_view(request,*args, **kagrs):
    blog = Blog.objects.all()
    content = { 'blog'  :   blog }
    return render(request,"contact.html", content )


def handle_page_not_found(request, exception=None):
    return redirect('home')