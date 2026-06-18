from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from .models import Category, Product, Cart, CartItem, Order


User = get_user_model()


class UserManagementTests(APITestCase):
    def test_create_user(self):
        url = '/api/users'
        data = {
            'username': 'tester',
            'email': 'tester@example.com',
            'password': 'safe-password-123',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username='tester').count(), 1)

    def test_create_admin_user_requires_staff(self):
        admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='adminpass')
        self.client.login(username='admin', password='adminpass')
        url = '/api/users'
        data = {
            'username': 'adminuser',
            'email': 'adminuser@example.com',
            'password': 'admin-password-123',
            'is_staff': True,
            'is_superuser': True,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='adminuser')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_change_password(self):
        user = User.objects.create_user(username='tester2', email='tester2@example.com', password='old-pass-123')
        self.client.login(username='tester2', password='old-pass-123')
        url = f'/api/users/{user.pk}/change_password'
        data = {'old_password': 'old-pass-123', 'new_password': 'new-pass-456'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('new-pass-456'))

    def test_admin_set_password(self):
        admin = User.objects.create_superuser(username='admin2', email='admin2@example.com', password='adminpass2')
        user = User.objects.create_user(username='tester4', email='tester4@example.com', password='orig-pass-123')
        self.client.login(username='admin2', password='adminpass2')
        url = f'/api/users/{user.pk}/set_password'
        data = {'username': 'tester4', 'email': 'tester4@example.com', 'new_password': 'admin-reset-789'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.check_password('admin-reset-789'))

    def test_reset_password(self):
        User.objects.create_user(username='tester3', email='tester3@example.com', password='orig-pass-123')
        url = '/api/users/reset_password'
        data = {
            'username': 'tester3',
            'email': 'tester3@example.com',
            'new_password': 'reset-pass-789',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(username='tester3')
        self.assertTrue(user.check_password('reset-pass-789'))

    def test_user_login_and_token(self):
        """Test user login endpoint returns token"""
        user = User.objects.create_user(username='loginuser', email='login@example.com', password='login-pass-123')
        url = '/api/users/login'
        data = {'username': 'loginuser', 'password': 'login-pass-123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'loginuser')

    def test_user_profile_endpoint(self):
        """Test user profile endpoint requires authentication"""
        user = User.objects.create_user(username='profileuser', email='profile@example.com', password='prof-pass-123')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        url = '/api/users/me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')


class CartTests(APITestCase):
    def setUp(self):
        """Create user, token, product, and category for tests"""
        self.user = User.objects.create_user(username='cartuser', email='cart@example.com', password='cart-pass-123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price='29.99',
            inventory=100,
        )

    def test_get_user_cart(self):
        """Test getting current user's cart"""
        url = '/api/cart/me'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertIn('total', response.data)

    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        url = '/api/cart/add_item'
        data = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 1)

    def test_remove_item_from_cart(self):
        """Test removing item from cart"""
        # Add item first
        CartItem.objects.create(
            cart=Cart.objects.create(user=self.user),
            product=self.product,
            quantity=2
        )
        
        url = '/api/cart/remove_item'
        data = {'product_id': self.product.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)

    def test_clear_cart(self):
        """Test clearing entire cart"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        url = '/api/cart/clear'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)

    def test_checkout_from_cart(self):
        """Test converting cart to order"""
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        url = '/api/cart/checkout'
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        # Verify cart is cleared
        cart.refresh_from_db()
        self.assertEqual(cart.items.count(), 0)


class OrderTests(APITestCase):
    def setUp(self):
        """Create user, token, product, and category for tests"""
        self.user = User.objects.create_user(username='orderuser', email='order@example.com', password='order-pass-123')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=self.category,
            price='49.99',
            inventory=50,
        )

    def test_list_user_orders(self):
        """Test user sees only their own orders"""
        order = Order.objects.create(
            user=self.user,
            customer_name='Order User',
            customer_email='order@example.com',
            status='paid'
        )
        
        url = '/api/orders'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], order.id)

    def test_pagination(self):
        """Test pagination in product list"""
        for i in range(25):
            Product.objects.create(
                name=f'Product {i}',
                slug=f'product-{i}',
                category=self.category,
                price='19.99',
                inventory=10,
            )
        
        url = '/api/products'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        # PAGE_SIZE is 20 in settings
        self.assertEqual(len(response.data['results']), 20)


class ProductSearchTests(APITestCase):
    def setUp(self):
        """Create test products"""
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product1 = Product.objects.create(
            name='Wireless Headphones',
            slug='wireless-headphones',
            description='High quality wireless headphones',
            category=self.category,
            price='79.99',
            inventory=20,
        )
        self.product2 = Product.objects.create(
            name='USB-C Charger',
            slug='usb-c-charger',
            description='Fast charging adapter',
            category=self.category,
            price='29.99',
            inventory=50,
        )

    def test_search_products_by_name(self):
        """Test searching products by name"""
        url = '/api/products?search=Wireless'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Wireless Headphones')

    def test_order_products_by_price(self):
        """Test ordering products by price"""
        url = '/api/products?ordering=price'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prices = [float(p['price']) for p in response.data['results']]
        self.assertEqual(prices, sorted(prices))
