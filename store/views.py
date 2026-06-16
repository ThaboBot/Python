from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from .models import Category, Product, Order
from .forms import OrderForm
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    OrderSerializer,
    UserSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
)


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(request, 'store/category_products.html', {
        'category': category,
        'products': products,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {
        'product': product,
    })


def checkout(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                customer_name=form.cleaned_data['customer_name'],
                customer_email=form.cleaned_data['customer_email'],
                status='draft',
            )
            order.items.create(
                product=product,
                quantity=form.cleaned_data['quantity'],
                unit_price=product.price,
            )
            return redirect(reverse('store:order_success', args=[order.id]))
    else:
        form = OrderForm()

    return render(request, 'store/checkout.html', {
        'product': product,
        'form': form,
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_success.html', {
        'order': order,
    })




User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'reset_password']:
            return [permissions.AllowAny()]
        if self.action == 'change_password':
            return [permissions.IsAuthenticated()]
        if self.action == 'set_password':
            return [permissions.IsAdminUser()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        user = self.get_object()
        if request.user != user and not request.user.is_staff:
            return Response({'detail': 'You may only change your own password.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if request.user == user:
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password.']}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def set_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Password set successfully.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset_password(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password reset successfully.'}, status=status.HTTP_200_OK)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
