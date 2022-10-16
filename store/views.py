from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
# from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from .serializers import *
from .models import Category, OrderItem, Product, Review
from .paginations import ProductPagination


# CRUD VIEWSETS
# Inherit from ReadOnlyModelViewSet if you don't need CUD
class ProductViewSet(ModelViewSet):
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

    # def destroy(self, request, *args, **kwargs):
    #     if Product.objects.filter(category_id=kwargs['pk']).count() > 0:
    #         return Response({'error': 'Category has been assigned to some products and hence, cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     return super().destroy(request, *args, **kwargs)


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
