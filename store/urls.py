from posixpath import basename
import pprint
from django.urls import include, path
from . import views
# from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers


# ue can use default route to show urls at the route when ue add .json at the end get all the products in json
#  To make nested routes get django drf-nested-routers
# router = SimpleRouter()
router = routers.DefaultRouter()
router.register('product',views.ProductViewSet)
router.register('collections',views.CollectionViewSet)

products_router = routers.NestedDefaultRouter(router,'products',lookup='product_pk')
products_router.register('reviews',views.ReviewViewSet,basename='product-reviews')
# pprint(router.urls)
# URLConf


# urlpatterns = router.urls 
urlpatterns = [
path('',include(router.urls)),
path('',include(products_router.urls)),
]
# urlpatterns = [
#     path('products/', views.ProductList.as_view),
#     path('products/<int:pk>', views.product_detail),
#     path('collections/<int:pk>', views.collection_detail,name="collection-detail"),
# ]
