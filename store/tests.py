from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


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
