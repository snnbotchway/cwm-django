from .views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('categories', CategoryViewSet)
router.register('customers', CustomerViewSet)
router.register('carts', CartViewSet, basename='carts')

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-review')

carts_router = routers.NestedDefaultRouter(
    router, 'carts', lookup='cart'
)
carts_router.register('cartitems', CartItemViewSet, basename='cart-cartitems')

urlpatterns = router.urls + products_router.urls + carts_router.urls
