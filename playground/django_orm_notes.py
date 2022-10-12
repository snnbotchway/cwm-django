from django.db.models import Avg, Min, Max, Sum, Count, Value, F, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType
from store.models import *
from tags.models import TaggedItem

# customers with .com in their email
customers = Customer.objects.filter(email__contains='.com')

# categories without a featured product
categories = Category.objects.filter(featured_product__isnull=True)

# product with inventory less than 10
products = Product.objects.filter(inventory__lt=10)

# all orders from customer with id 1
orders = Order.objects.filter(customer_id=1)

# all orderItems from category 3
orderItems = OrderItem.objects.filter(product__category=3)

# all products that have been ordered at least once sorted according to title
products = OrderItem.objects.values(
    'product__title').order_by('product__title').distinct()

# count of all orders that have an id(all orders in this case)
totalOrders = Order.objects.aggregate(Count('id'))

# total number of product 1 units sold
sold1 = OrderItem.objects.filter(
    product_id=1).aggregate(sum_of_all_1=Sum('quantity'))

# count of all orders from customer 1 that have an id(all orders in this case)
orders1 = Order.objects.filter(
    customer_id=1).aggregate(orders_count=Count('id'))

# Min, Max and Avg price of all products from category 3
c3 = Product.objects.filter(category_id=3).aggregate(
    min_price=Min('unit_price'), max_price=Max('unit_price'), avg_price=Avg('unit_price'))

# customer table with new field id+1 as new_id
customers = Customer.objects.annotate(new_id=F('id')+1)

# Visit https://docs.djangoproject.com/en/4.1/ref/models/database-functions/ for more
# customer table with new full name field (first_name + last_name)
customers = Customer.objects.annotate(full_name=Func(
    F('first_name'), Value(' '), F('last_name'), function='CONCAT'))
# or
customers = Customer.objects.annotate(
    full_name=Concat('first_name', Value(' '), 'last_name'))

# number of orders each customer has placed
customers = Customer.objects.annotate(
    order_count=Count('order')
)

# product table with new field name discounted_price(unit_price * 0.8)
discounted_price = ExpressionWrapper(
    F('unit_price')*0.8, output_field=DecimalField())
products = Product.objects.annotate(
    discounted_price=discounted_price
)

# get all tags for product 1 (Querying generic relationships)
# 1. get content_type id of products
content_type = ContentType.objects.get_for_model(Product)
# 2. tagged items can now be queried with content_type id and object_id
tags = TaggedItem.objects.filter(
    content_type_id=content_type,
    object_id=1
).\
    select_related('tag')

# or 1.
tags = TaggedItem.objects.get_tags_for(Product, 1)
# 2. define the following in tags models.py


class TaggedItemManager(models.Manager):
    def get_tags_for(self, object_type, object_id):
        content_type = ContentType.objects.get_for_model(object_type)
        return TaggedItem.objects.filter(
            content_type_id=content_type,
            object_id=object_id
        ).\
            select_related('tag')


# 3. define in TaggedItem model:
objects = TaggedItemManager()
