from .views import *
from rest_framework_nested import routers

router = routers.DefaultRouter()
router.register('products', ProductViewSet, basename='products')
router.register('categories', CategoryViewSet)
router.register('customers', CustomerViewSet)
router.register('carts', CartViewSet, basename='carts')
router.register('orders', OrderViewSet, basename='orders')

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-review')
products_router.register('images', ProductImageViewSet,
                         basename='product-image')

carts_router = routers.NestedDefaultRouter(
    router, 'carts', lookup='cart'
)
carts_router.register('cartitems', CartItemViewSet, basename='cart-cartitems')

orders_router = routers.NestedDefaultRouter(
    router, 'orders', lookup='order'
)
# orders_router.register('orderitems', OrderItemViewSet, basename='order-orderitems')

urlpatterns = router.urls + products_router.urls + \
    carts_router.urls + orders_router.urls
