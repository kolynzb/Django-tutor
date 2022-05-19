from django.shortcuts import get_object_or_404
from django.http import HttpResponse

# from rest_framework.decorators import api_view
from rest_framework.response import Response
from models import Product
from store import serializers
from store.filters import ProductFilter
from store.models import Collection, OrderItem, Review
from store.serializers import CollectionSerializer, ProductSerializer, ReviewSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
# Create your views here.

#class based view
class ProductList(ListCreateAPIView):
    queryset=Product.objects.select_related('collection').all()
    serializer_class=ProductSerializer
    def get_serializer_context(self):
        return {"request":self.request}


# #class based view
# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.select_related('Collections').all()
#         serializer = ProductSerializer(queryset,many=True,context={'request': request})
#         return Response(serializer.data)
#     def post(self,request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response('ok')

class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request,pk):
        product =get_object_or_404( Product,pk=pk)  
        if product.orderitem_set.count() > 0:
            return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class ProductDetailWithFilter(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset= Product.objects.all()
        collection_id =  self.request.query_params.get('collection_id')
        if collection_id is not None :
            queryset = queryset.filter(collection_id=collection_id)
        return queryset

    def delete(self, request,pk):
        product =get_object_or_404( Product,pk=pk)  
        if product.orderitem_set.count() > 0:
            return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
# For generic filters use `pipenv install django-filter` then add django_filters to your list of installed apps 
class ProductDetailWithGenericFilter(RetrieveUpdateDestroyAPIView):
    queryset= Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields =['collection_id']
    #  for custome filters use django filter .io to create a range  for ,'unit_price'

    def delete(self, request,pk):
        product =get_object_or_404( Product,pk=pk)  
        if product.orderitem_set.count() > 0:
            return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class ProductDetailWithGenericAndSearchFilterAndSortAndPagination(RetrieveUpdateDestroyAPIView):
    queryset= Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    filterset_class =ProductFilter
    search_fields =['title','description']
    orderingfields =['unit_price','last_update']
    pagination_class = PageNumberPagination
    #  for customer filters use django filter .io to create a range  for ,'unit_price'

    def delete(self, request,pk):
        product =get_object_or_404( Product,pk=pk)  
        if product.orderitem_set.count() > 0:
            return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# class ProductDetail(APIView):
#     def get(self, request,id):
#         product =get_object_or_404( Product,pk=id)  
#         serializer= ProductSerializer(product)
#         return Response(serializer.data)
#     def put(self, request,id):
#         product =get_object_or_404( Product,pk=id)  
#         serializer = ProductSerializer(product,data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(serializer.data,status=status.HTTP_200_OK)
#     def delete(self, request,id):
#         product =get_object_or_404( Product,pk=id)  
#         if product.orderitem_set.count() > 0:
#             return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
    
# combines product and product details
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        return {'request':self.request}
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response({'error':"Product cannot be deleted because it is associated with an order item"},status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer = CollectionSerializer
    # used to passs values to the serializer
    def get_serializer_context(self):
        return {"request":self.request}

    def delete(self, request,pk):
        collection = get_object_or_404(Collection,pk=pk) 

        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# @api_view()
# def collection_detail(request,pk):
#     collection = Collection.objects.get(pk=pk)
#     serializer=CollectionSerializer(collection)
#     return Response(serializer.data)

class ReviewViewSet(ModelViewSet):
    serializer = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

    