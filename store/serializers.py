from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Category, Product, Order, OrderItem, Cart, CartItem


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_staff', 'is_superuser', 'is_active']
        read_only_fields = ['id']

    def validate(self, attrs):
        request = self.context.get('request')
        admin_fields = {'is_staff', 'is_superuser', 'is_active'}
        if any(field in attrs for field in admin_fields):
            if not request or not request.user.is_authenticated or not request.user.is_staff:
                raise serializers.ValidationError('Only staff users may set staff, superuser, or active flags.')
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance


class UserProfileSerializer(serializers.ModelSerializer):
    """Simplified user profile for customers"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class LoginSerializer(serializers.Serializer):
    """Login serializer for token auth"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)


class PasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(write_only=True, required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'inventory', 'is_active', 'category', 'category_id', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product', write_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal']

    def get_subtotal(self, obj):
        return str(obj.get_subtotal())


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'updated_at']

    def get_total(self, obj):
        return str(obj.get_total())


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'customer_email', 'status', 'created_at', 'items', 'total']
        read_only_fields = ['created_at']

    def get_total(self, obj):
        return str(obj.get_total())

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.customer_email = validated_data.get('customer_email', instance.customer_email)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
        return instance
