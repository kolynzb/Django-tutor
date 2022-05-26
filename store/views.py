from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from html5lib import serialize


from rest_framework.decorators import api_view,action
from rest_framework.response import Response

from store.permissions import IsAdminOrReadOnly
from .models import Cart, CartItem, Customer, Order, Product
from store import serializers
from store.filters import ProductFilter
from store.models import Collection, OrderItem, Review
from store.serializers import AddCartItemSerializer, AddCartSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,UpdateModelMixin
from rest_framework.permissions import IsAuthenticated,AllowAny
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
    permission_classes=[IsAdminOrReadOnly]

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


# creating a custom view that only creates ,reads and  deletes 
class CartViewSet(CreateModelMixin,RetrieveModelMixin,DestroyModelMixin,GenericViewSet):
    # prefetch since therelated guys are mob 
    queryset= Cart.objects.prefetch_related('items__product').all()
    serializer = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names =  ['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method == 'POST': 
            return AddCartItemSerializer
        if self.request.method == 'PATCH': 
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_id'],}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs(['cart_pk'])).select_related('product') 

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes =[FullDjangoModelPermissions]

# always add permissions to groups then add users to those groups
    @action(detail=True,permission_classes=['ViewCustomerHistoryPermission'])
    def history(self, request, pk):
        return Response('Ok')

    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    # available on list false on detail view true
    def me(self,request):
        (customer,created_at)=Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exceptions=True)
            serializer.save()
            return Response(serializer.data)
# class CustomerViewSet(CreateModelMixin,RetrieveModelMixin,UpdateModelMixin,GenericViewSet):
#     queryset = Customer.objects.all()
#     serializer_class = CustomerSerializer
#     # permission_classes =[IsAuthenticated]

#     def get_permissions(self):
#         if  self.request.method == 'GET':
#             return[AllowAny()]
#         return [IsAuthenticated()]

#     @action(detail=False,methods=['GET','PUT'])
#     # available on list false on detail view true
#     def me(self,request):
#         (customer,created_at)=Customer.objects.get_or_create(user_id=request.user.id)
#         if request.method == 'GET':
#             serializer = CustomerSerializer(customer)
#             return Response(serializer.data)
#         elif request.method == 'PUT':
#             serializer = CustomerSerializer(customer,data=request.data)
#             serializer.is_valid(raise_exceptions=True)
#             serializer.save()
#             return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    http_method_names=['get','patch','delete','head','options']
    def get_permissions(self):
        if self.request.method in ['PUT','PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    def create(self, request):
        serializer = CreateOrderSerializer(data=request.data,context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exceptions=True)
        order =serializer.save()
        serializer=OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        if self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer
    # def get_serializer_context(self):
    #     return {'user_id':self.request.user.id}
    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        (customer_id,created)=Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)

# Command Query Separation Principle

            

