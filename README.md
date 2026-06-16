# Django Store API

This repository contains a Django REST Framework project for a simple store application.

## Project Structure

- `manage.py` - Django management utility
- `store_api/` - Django project settings and URL configuration
- `store/` - Django app containing models, serializers, views, and tests

## Key Features

- Category, product, and order CRUD via REST API
- User management API for:
  - creating users
  - resetting passwords
  - changing passwords
  - admin user creation and admin password management
- Django admin available at `/admin/`

## Installed Apps

- `django.contrib.admin`
- `django.contrib.auth`
- `django.contrib.contenttypes`
- `django.contrib.sessions`
- `django.contrib.messages`
- `django.contrib.staticfiles`
- `rest_framework`
- `store`

## Models

- `Category`
- `Product`
- `Order`
- `OrderItem`

## API Endpoints

The API is exposed under `/api/` using DRF's router.

### Categories

- `GET /api/categories` - list categories
- `POST /api/categories` - create category
- `GET /api/categories/{slug}` - retrieve category
- `PUT /api/categories/{slug}` - update category
- `PATCH /api/categories/{slug}` - partial update category
- `DELETE /api/categories/{slug}` - delete category

### Products

- `GET /api/products` - list active products
- `POST /api/products` - create product
- `GET /api/products/{slug}` - retrieve product
- `PUT /api/products/{slug}` - update product
- `PATCH /api/products/{slug}` - partial update product
- `DELETE /api/products/{slug}` - delete product

### Orders

- `GET /api/orders` - list orders
- `POST /api/orders` - create order
- `GET /api/orders/{id}` - retrieve order
- `PUT /api/orders/{id}` - update order
- `PATCH /api/orders/{id}` - partial update order
- `DELETE /api/orders/{id}` - delete order

### Users

- `POST /api/users` - create a new user
- `GET /api/users` - list users (admin only)
- `GET /api/users/{id}` - retrieve user (admin only)
- `PUT /api/users/{id}` - update user (admin only)
- `PATCH /api/users/{id}` - partial update user (admin only)

### Password Management

- `POST /api/users/reset_password` - reset password using username and email
- `POST /api/users/{id}/change_password` - change password for authenticated users
- `POST /api/users/{id}/set_password` - set password directly for admin users

## Admin

Visit the admin dashboard at:

- `http://127.0.0.1:8090/admin/`

If no admin user exists, create one using:

```powershell
& "f:/Documents/Projects Worked On/Python/venv/Scripts/python.exe" manage.py createsuperuser
```

## How to run

1. Open PowerShell in the project root:

```powershell
Set-Location -Path "F:\Documents\Projects Worked On\Python"
```

2. Activate the virtual environment:

```powershell
& "f:/Documents/Projects Worked On/Python/venv/Scripts/Activate.ps1"
```

3. Start the Django development server on port `8090`:

```powershell
& "f:/Documents/Projects Worked On/Python/venv/Scripts/python.exe" manage.py runserver 8090
```

4. Open the app in your browser:

- `http://127.0.0.1:8090/`
- admin: `http://127.0.0.1:8090/admin/`

## Tests

Run the app tests with:

```powershell
& "f:/Documents/Projects Worked On/Python/venv/Scripts/python.exe" manage.py test store
```

## Notes

- The server is currently configured to run on port `8090` due to local port restrictions.
- Passwords are stored securely using Django's password hashing.
