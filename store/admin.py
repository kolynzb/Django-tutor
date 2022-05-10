from django.contrib import admin
from . import models


# Customise list pages 

# Register your models here.
admin.site.register(models.Collection)
admin.site.register(models.Product)