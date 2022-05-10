from django.contrib import admin
from . import models


# Customise list pages 
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','unit_price']
    list_editable = ['unit_price'] #allows editing on a particularfeild 
    list_per_page = 10 #Ten items per page
    # Google django model admin options
# admin.site.register(models.Product,ProductAdmin)


# Register your models here.
admin.site.register(models.Collection)