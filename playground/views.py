from typing import Collection
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from store.models import Order, OrderItem, Product
from tags.models import TaggedItem, TaggedItemManager
from django.db import connection, transaction

def say_hello(request):

    
    queryset = Product.objects.filter(pk=1).first()
    return render(request, 'hello.html', {'name': 'Mosh','products':list(queryset)})

'''
Product.obejct.something returns a queryset that is evaluated and changed to sql
queryset api
'''

def query_generic_relationships(request):
    # Finding contentype ID for the product
    contentType = ContentType.objects.get_for_model(Product)

    query_set=TaggedItem.objects \
    .select_related('tag') \
    .filter(
        contentType=contentType,
        object_id=1)

    return render(request, 'hello.html', {'name': 'Mosh','products':list(query_set)})

def create_obj(request):
    collection = Collection()
    collection.title = 'Video Games'
    collection.featured_product=Product(pk=1)
    # collection.featured_product_id=1
    collection.save()
    
def create_obj2(request):
    collection = Collection(title = 'Video Games')
    # collection.featured_product=Product(pk=1)
    # collection.featured_product_id=1

def create_obj3(request):
    collection = Collection.objects.create(title = 'Video Games',featured_product_id=1)

def update_obj(request):
    collection = Collection.objects.get(pk=11)
    collection.featured_product = None
    collection.save()

def update_obj2(request):
    collection = Collection.objects.filter(pk=11).update(featured_product = None)
    
def delete_obj(request):
    collection = Collection(pk=11)
    collection.delete()
    # delete objects
    Collection.objects.filter(id_gt=11).delete()
    
def transaction_t(request):
    # if one operation fails we want everything to be rolled back

    with transaction.atomic():
        order = Order()
        order.customer_id=10
        order.save()

        item= OrderItem()
        item.order=order
        item.product_id=11
        item.quantity=11
        item.unit_price=10
        item.save()
   
def raw_sql(request):
    query_set=Product.objects.raw('SELECT * FROM store_product')

def raw_sql2(request):
    # use a try finally block or with
    cursor = connection.cursor()
    cursor.execute('')
    cursor.close()

    # or
    with connection.cursor() as cursor:
        # cursor.callproc('get_cutomers',[1,2,'a'])  stored procedures
        cursor.execute('')
    