from xml.etree.ElementInclude import include
from .views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('categories', CategoryViewSet)
router.register('carts', CartViewSet, basename='carts')

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-review')

urlpatterns = router.urls + products_router.urls
