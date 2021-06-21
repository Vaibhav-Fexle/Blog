from random import random, randint

from django.core.management import BaseCommand
from faker import Faker, providers

from blog.models import *

CATEGORIE = ['Art', 'Animals', 'Clothing', 'Dairy Products', 'Drinks', 'Emotions', 'Foods', 'Fruits','Furniture', 'Insects',
             'Jobs', 'Kitchen', 'Tools', 'Meats', 'Musical Instruments', 'Music', 'Places', 'Shapes', 'Sports', 'Vegetables',
             'Transportation', 'Colors', 'Holidays', 'Seasons', 'Christmas', 'Winter', 'Easter', 'Spring', 'Flag', 'Memorial',

             'Halloween', 'New Year', 'Summer']


import os

class Providers(providers.BaseProvider):

    def blog_categorie(self):
        return self.random_element(CATEGORIE)

    def categorie(self):
        return self.random_element(Categories.objects.all())

    def blogger(self):
        return self.random_element(Blogger.objects.filter(is_staff=False, is_blogger=False))

    def blog_blogger(self):
        return self.random_element(Blogger.objects.filter(is_blogger=True))

    def viewer(self):
        return self.random_element(Blogger.objects.all())
    def blog(self):
        return self.random_element(Blog.objects.all())


class Command(BaseCommand):
    help = 'command info'

    def handle(self, *args, **kwargs):

        img = 30
        maxcom = 40
        faker = Faker(['en'])
        faker.add_provider(Providers)

        ## create categories 30

        for i in range(30):
            d = faker.unique.blog_categorie()
            cat = Categories.objects.create(title=d, description=d)
            print('Categories -',cat)

        ##      create viewer (user) 1000+300+30 ~~= 1400~1500
        for i in range(1400):
            data = faker.profile()
            name = data['username']
            user = User.objects.create(username=f'{name}{str(randint(0,9))}{str(randint(0,9))}', email=data['mail'], first_name=data['name'])
            print('User -',user.username)
            user.set_password('1234test')

            bio=faker.text(max_nb_chars=50)
            pic = randint(0,img)
            Blogger.objects.create(user=user, bio=bio, website=data['website'][0],
                                      user_pic=f'static/color/{pic}.jpg')

        ##      create blogger 300
        for i in range(300):
            user = faker.unique.blogger()
            user.is_blogger = True
            user.save()
            print('blogger -', user)

        ##      create staff 30
        for i in range(30):
            user = faker.unique.blogger()
            user.is_blogger = True
            user.is_staff = True
            user.save()
            print('staff -',user)

        ##      create blog 3000
        for i in range(3000):
            title = faker.text(max_nb_chars=15)
            des = faker.text(max_nb_chars=300)
            owner = faker.blog_blogger()
            pic = randint(0,img)
            photo = f'static/color/{pic}.jpg'

            pic = randint(1, 6)
            cat = [faker.categorie() for i in range(pic)]

            blog = Blog.objects.create(title=title, description=des,
                                       owner=owner.user, photo=photo )
            blog.categorie.set(cat)
            blog.save()
            print('blog -', blog.title)



        for i in Blog.objects.all():
            count = randint(5, maxcom)
            for j in range(count):
                user = faker.viewer()
                text = faker.text(max_nb_chars=100)
                Comment.objects.create(blog=i, owner=user.user, description=text )
            i.save()

            print('comment -',i)


