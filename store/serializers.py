from decimal import Decimal
from rest_framework import serializers

from store.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'products_count']
    products_count = serializers.SerializerMethodField(
        method_name='get_products_count')

    def get_products_count(self, category: Category) -> int:
        return category.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'unit_price',
                  'description', 'inventory', 'price_inc_tax', 'category']

    price_inc_tax = serializers.SerializerMethodField(
        method_name='get_price_with_tax')
    # string related field for relationship
    # category = serializers.StringRelatedField()
    # for object field:
    # category = CategorySerializer()

    # for hyperlink to relationship detail:
    # category = serializers.HyperlinkedRelatedField(
    #     queryset=Category.objects.all(),
    #     view_name='category_detail',
    # )

    def get_price_with_tax(self, product: Product) -> Decimal:
        return product.unit_price * Decimal(1.1)

    # validation method example for password == confirm_password
    # def validate(self, data):
    #     if data['password'] == data['confirm_password']:
    #         return data
    #     else:
    #         return serializers.ValidationError('Passwords do not match!')

    # overriding the create method which serializer.save() calls
    # def create(self, validated_data):
        # product variable created by combining the model and validated data
        # product = Product(**validated_data)
        # additional fields can be added through computations
        # force every inventory to be one:
        # product.inventory = 1 # the one here could be computed based on other values and not hardcoded
        # product.save()
        # return product

    # overriding the update method which serializer.save() calls
    # def update(self, instance: Product, validated_data):
        # updating the unit price of a product for example:
        # instance.unit_price = validated_data.get('unit_price') + 1
        # instance.save()
        # return instance
