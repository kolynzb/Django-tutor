from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from models import Product
from store import serializers
from store.models import Collection
from store.serializers import CollectionSerializer, ProductSerializer
from rest_framework import status
from rest_framework.views import APIView
# Create your views here.

@api_view(['GET','POST'])
def product_list(request):
    if request.method == 'GET':
        queryset = Product.objects.select_related('Collections').all()
        serializer = ProductSerializer(queryset,many=True,context={'request': request})
        # many iterates over the queryset 
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.validated_data
        serializer.save()
        return Response('ok')

@api_view()
def product_detail(request,id):
    try:
        product = Product.objects.get(pk=id)
        # Serializing Object 
        serializer= ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PUT','DELETE'])
def product_detail_withShortCut(request,id):
    # this wraps the try catch logic 
    product =get_object_or_404( Product,pk=id)  
    if request.method == 'GET':
        serializer= ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product,data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        if product.orderitem_set.count() > 0:
            return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
@api_view()
def collection_detail(request,pk):
    collection = Collection.objects.get(pk=pk)
    serializer=CollectionSerializer(collection)
    return Response(serializer.data)

#class based view
class ProductList(APIView):
    def get(self, request):
        queryset = Product.objects.select_related('Collections').all()
        serializer = ProductSerializer(queryset,many=True,context={'request': request})
        return Response(serializer.data)
    def post()