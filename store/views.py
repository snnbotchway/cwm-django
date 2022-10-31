from urllib import request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Count
# from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from store.permissions import IsAdminOrReadOnly
from .filters import *
from .serializers import *
from .models import Category, Customer, Order, OrderItem, Product, Review, Cart
from .paginations import ProductPagination


# CRUD VIEWSETS
# Inherit from ReadOnlyModelViewSet if you don't need CUD
class ProductViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = ProductSerializer

    # automatic filtering with url params:
    # def get_queryset(self):
    #     if self.request.query_params.get('category_id'):
    #         return Product.objects.filter(category_id=self.request.query_params.get('category_id'))
    #     return Product.objects.all()
    # or when filters get many (better way): set queryset to .all and:
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = ProductPagination
    search_fields = ['title', 'description', 'category__title']
    ordering_fields = ['unit_price', 'last_updated']
    # then create filters.py and create ProductFilter

    def get_context_data(self, request):
        return {'context': request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product has been ordered before and hence, cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CategoryViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.annotate(
        product_count=Count('products')
    )
    serializer_class = CategorySerializer

    def get_context_data(self, request):
        return {'context': request}

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(category_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Category has been assigned to some products and hence, cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    # get the product id from the url:
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    # give the serializer the product id from the url:

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.prefetch_related('cartitems__product').all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch',
                         'delete']  # to prevent put requests

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return AddCartItemSerializer

    # get the cart id from the url:
    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['cart_pk'])
    # give the serializer the cart id from the url:

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    # extend and customize DjangoModelPermissions to use group permissions
    # To apply custom permissions, create in model meta, create in permissions.py and apply here
    permission_classes = [IsAdminUser]

    # configure /customers/me/ action to get current user profile
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        (customer, created) = Customer.objects.get_or_create(
            user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        # only admins should be able to update or delete order
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    # override to return saved order instead of cartId
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        headers = self.get_success_headers(serializer.data)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.prefetch_related('orderitems__product').all()
        (customer_id, created) = Customer.objects.only(
            'id').get_or_create(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id).prefetch_related('orderitems__product')


# CRUD GENERIC VIEWS
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_context_data(self, request):
#         return {'context': request}

    # or
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     return queryset

    # def get_serializer_class(self):
    #     return ProductSerializer
# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     serializer_class = ProductSerializer
#     queryset = Product.objects.all()

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product has been ordered before and hence, cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         self.product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD CLASS BASED VIEWS
# class ProductList(APIView):
#     def get(self, request):
#         products = Product.objects.prefetch_related('category').all()
#         serializer = ProductSerializer(
#             products, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         serializer = ProductSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# class ProductDetail(APIView):
#     def get(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(
#             product, many=False, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product has been ordered before and hence, cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         self.product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# CRUD FUNCTION BASED VIEWS
# from rest_framework.decorators import api_view
# @api_view(['GET', 'POST'])
# def category_list(request):
#     if request.method == 'GET':
#         categories = Category.objects.prefetch_related(
#             'products').all().order_by('id')
#         serializer = CategorySerializer(
#             categories, many=True, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         serializer = CategorySerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'PUT', 'DELETE'])
# def category(request, pk):
#     category = get_object_or_404(Category, id=pk)
#     if request.method == 'GET':
#         serializer = CategorySerializer(
#             category, many=False, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'PUT':
#         serializer = CategorySerializer(category, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'DELETE':
#         if category.products.count() > 0:
#             return Response({'error': 'Category has been assigned to some products and hence, cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         category.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
