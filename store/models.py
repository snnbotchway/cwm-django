from django.db import models
from django.core.validators import MinValueValidator


class Promotion(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, blank=True, null=True, related_name='+')

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    inventory = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)

    class Meta:
        ordering = ['title']

    def __str__(self) -> str:
        return self.title


class Customer(models.Model):
    BRONZE = 'B'
    SILVER = 'S'
    GOLD = 'G'
    MEMBERSHIP_CHOICES = [
        (BRONZE, 'Bronze'),
        (SILVER, 'Silver'),
        (GOLD, 'Gold'),
    ]
    membership = models.CharField(
        max_length=1,
        choices=MEMBERSHIP_CHOICES,
        default=BRONZE,
    )
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    birth_date = models.DateField(null=True)
    phone = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['first_name', 'last_name']


class Order(models.Model):
    PENDING = 'P'
    COMPLETE = 'C'
    FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    ]
    payment_status = models.CharField(
        max_length=1,
        choices=PAYMENT_STATUS_CHOICES,
        default=PENDING,
    )
    placed_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.customer)

    class Meta:
        ordering = ['placed_at', 'customer']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    zip = models.PositiveIntegerField(null=True)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
