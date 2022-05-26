from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from decimal import Decimal
from store import models
from store.models import Cart, CartItem, Customer, Order, OrderItem, Product,Collection, Review
from django.db import transaction
from .signals import order_created

# # serializers convert a model instance to a dictionary
# class ProductSerializer(serializers.Serializer):
#     # map out each feild that the user will want to access or update
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2,source='unit_price')
#     price_with_tax=serializers.SerializerMethodField()
#     # to serialize a relationship 
#     # collection = CollectionSerializer()
#     collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all())
#     # collection = serializer.HyperlinkedRelatedField(queryset=Collection.objects.all(),view_name='collection-details')

    # def calculate_tax(self,product:Product):
    #     return product.unit_price * Decimal(1.1)
# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id','title']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        feilds = ['id','title','unit_price','collection','slug','inventory','description']
    # collection = CollectionSerializer()
    price_with_tax=serializers.SerializerMethodField(method_name="calculate_tax")
    def calculate_tax(self,product:Product):
        return product.unit_price * Decimal(1.1)
    ##  overide product validation
    # def validate(self,data):
    #     if data['password'] != data['confirm_password']:
    #         return serializers.ValidationError('Passwords Dont Match')
    #     return data

    # overide product creation
    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other=1
    #     product.save()
    #     return product

    # Overide updated
    # def update(self,instance,validated_data):
    #     instance.unit_price = validated_data.get('unit_price')
    #     instance.save()
    #     return instance

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        feilds = ['id','date','name','description']
    
    # adding the id that was added to the route
    def create(self,validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id,**validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']
class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart_item:CartItem):
        return cart_item.quantity * cart_item.unit_price
    class Meta:
        model=models.CartItem
        fields=['id','product','quantity']
class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items=CartItemSerializer(many=True,read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self,cart:Cart):
        #list comprehension
        return sum([item.quantity * item.product.unit_price  for item in cart.items.all()])    
    class Meta:
        model=models.Cart
        fields=['id','items','total_price'] #only return the id

# This serializer is for updatng products in a cart 
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    # validate to prevent app from crashing when given a wrong id or negative quantity
    # to validate a field use the validate_name_of_feild
    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No Product Exists with this ID')
        return value

    # we overide save method since we want to update the quantity when the same product is added again
    def save(self, **kwargs):
        cart_id = self.context["cart_id"]
        product_id = self.validated_data['product_id'] 
        quantity = self.validated_data['quantity'] 
        try:
            #Update Quantity 
            cart_item= CartItem.objects.get(product_id=product_id, cart_id=cart_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # save new cart
            self.instance=CartItem.objects.create( cart_id=cart_id,**self.validated_data)
        return self.instance
    class Meta:
        model=CartItem
        fields=['id','product_id','quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    model = CartItem
    fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user_id= serializers.IntegerField(read_only=True )
    class Meta:
        model = Customer
        fields = ['id','user_id','phone','birth_date','membership']
        
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = models.OrderItem
        fields=['id','product','unit_price','quantity']
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    class Meta:
        model = models.Order
        fields=['id','placed_at','customer','payment_status','items']

class CreateOrderSerializer(serializers.BaseSerializer):
    card_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("No Cart with this ID was Found")
        if CartItem.objects.filter(pk=cart_id).count() == 0:
            raise serializers.ValidationError("The Cart Is Empty")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(user_id=self.context['user_id'])
            order=Order.objects.create(customer=customer)
            cart_items = CartItem.objects \
                .select_related('product') \
                .filter(cart_id=self.validated_data['cart_id'])
            order_items = [
                OrderItem(
                    order = order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
            ) for item in cart_items]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

            order_created.send_robust(self.__class__,order=order)
            return order

        

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields=['payment_status']
        

