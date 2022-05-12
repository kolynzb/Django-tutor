from django.contrib import admin,messages
from django.http import HttpRequest
from . import models
from django.utils.html import format_html,url_encode
from django.urls import reverse


# Customise list pages 
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','unit_price','inventory_status','collection_title'] #inventory status is a computed column while collection is a relation
    list_editable = ['unit_price'] #allows editing on a particularfeild 
    list_per_page = 10 #Ten items per page'
    list_select_related=["collection"] #eger loading the related feilds
    search_fields =['title__istartswith'] #add search box
    action=["clear_inventory"] # define actions
    # feilds=['title','slug'] #fields for adding
    # exclude=['title','slug'] #fields for exclusion
    # readonly=['title','slug'] #fields for read only
    prepopulated_fields={'slug':['title','...']} 
    autocomplete_fields=['collection'] # mKE SURE TO SET SEARCH FEILDS IN COLLECTIONS
    # Google django model admin options

    def collection_title(self,product):
        return product.collection.title #get a particular feild 
    @admin.display(ordering="inventory") #for ordering 
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'LOW'
        return 'OK'
    
    # custom actions 
    @admin.action(description="Clear Inventory")
    def clear_inventory(self,request,queryset):
        updated_count=queryset.update(inventory=0)
        self.message_user(request,f'{updated_count} products were successfully uplloaded',
        messages.ERROR
        )





# admin.site.register(models.Product,ProductAdmin)


# Register your models here.
admin.site.register(models.Collection)

# overiding base query
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title','products_count']
    search_fields =['title']


    @admin.display(ordering='product_count')
    def products_count(self,collection):
        # reverse('admin:app_model_page')
        url =(reverse('admin:product_changeList')
         + '?' + 
         url_encode({
             'collection__id':str(collection.id),
         })
         )
        format_html('<a href="{}"> {}</a>',url,collection.products_count)
        return collection.products_count #But products count doesnot exits

    def get_queryset(self,request) :
        return super().get_queryset(request).annotate(products_count=Count('product'))

m#tabular and stackeed iline editing children
class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ['product',]
    extra = 0
    min_num=1
    max_num=10

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','placed_at','customer']
    inlines = [OrderItemInline]
    autocomplete_fields=['customer']