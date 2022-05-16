from rest_framework import serializers
from decimal import Decimal
from store.models import Product,Collection

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

