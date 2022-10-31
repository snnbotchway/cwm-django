from decimal import Decimal
from django.db.models import F
from django.db import transaction
from rest_framework import serializers
from django.conf import settings

from .models import CartItem, Category, Customer, Order, OrderItem, Product, Review, Cart


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product',
                  'unit_price', 'quantity']


class AddOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, value):
        # check if cart exists
        if not Cart.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'This cart does not exist.')
        # check if cart is empty (has no cart items associated with it)
        if CartItem.objects.filter(cart_id=value).count() == 0:
            raise serializers.ValidationError(
                'This cart is empty.')
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer = Customer.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.select_related(
                'product').filter(cart=cart_id)
            # using list comprehension to create list of order items from list of cart items
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    orderitems = OrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['id', 'payment_status',
                  'placed_at', 'customer', 'orderitems']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'date']

    def create(self, validated_data):
        return Review.objects.create(product_id=self.context['product_id'], **validated_data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'product_count']
    product_count = serializers.IntegerField(read_only=True)


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


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'birth_date', 'phone', 'user_id', 'membership']


class CartItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price')
    product = SimpleProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, cartitem: CartItem) -> Decimal:
        return cartitem.quantity * cartitem.product.unit_price


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']

    # ensure the product that is being added exists in the database
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'This product was not found in our database.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:  # update cart item if it exists
            cart_item = CartItem.objects.get(
                product_id=product_id, cart_id=cart_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:  # create a new cart item since one was not found
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)
        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    cartitems = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price')

    def get_total_price(self, cart: Cart):
        total_price = 0
        for item in cart.cartitems.all():
            total_price += item.quantity * item.product.unit_price
        return total_price

    class Meta:
        model = Cart
        fields = ['id', 'cartitems', 'total_price']
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
