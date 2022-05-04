from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product


def say_hello(request):

    
    queryset = Product.objects.filter(pk=1).first()
    return render(request, 'hello.html', {'name': 'Mosh','products':list(queryset)})

'''
Product.obejct.something returns a queryset that is evaluated and changed to sql
queryset api
'''