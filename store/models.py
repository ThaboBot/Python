from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Shopping cart for users before checkout"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Cart for {self.user.username}'

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())


class CartItem(models.Model):
    """Individual items in a shopping cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f'{self.quantity} x {self.product.name} in cart'

    def get_subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order {self.id} for {self.customer_name}'

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_subtotal(self):
        return self.quantity * self.unit_price
