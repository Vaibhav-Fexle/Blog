from django.core.management import BaseCommand
from faker import Faker, providers

from blogger.blog.models import *

CATEGORIE = ['Art', 'Animals', 'Clothing', 'Dairy Products', 'Drinks', 'Emotions', 'Foods', 'Fruits','Furniture',
             'Insects', 'Jobs', 'Kitchen', 'Tools', 'Meats', 'Musical Instruments', 'Music', 'Places', 'Shapes',
             'Sports', 'Vegetables', 'Transportation', 'Colors', 'Holidays', 'Seasons', 'Christmas', 'Winter', 'Easter',
             'Spring', 'Flag', 'Memorial', 'Halloween', 'New Year', 'Summer']

class Providers(providers.BaseProvider):

    def blog_categorie(self):
        return self.random_element(CATEGORIE)


class Command(BaseCommand):
    help = 'command info'

    def handle(self, *args, **kwargs):

        faker = Faker(['en'])
        faker.add_provider(Providers)

        print('--', faker.blog_categorie())
        #
        # for i in range(10):
        #     d= faker.unique.blog_categorie()
        #     Categories.objects.create(title=d, description=d)