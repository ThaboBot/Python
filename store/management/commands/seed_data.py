from django.core.management.base import BaseCommand
from store.models import Category, Product


class Command(BaseCommand):
    help = 'Seed the database with sample product data'

    def handle(self, *args, **options):
        # Create categories
        electronics, _ = Category.objects.get_or_create(
            name='Electronics',
            defaults={'slug': 'electronics'}
        )
        clothing, _ = Category.objects.get_or_create(
            name='Clothing',
            defaults={'slug': 'clothing'}
        )
        books, _ = Category.objects.get_or_create(
            name='Books',
            defaults={'slug': 'books'}
        )

        # Sample products
        products_data = [
            {
                'category': electronics,
                'name': 'Wireless Headphones',
                'slug': 'wireless-headphones',
                'description': 'High-quality wireless headphones with noise cancellation',
                'price': '79.99',
                'inventory': 50,
            },
            {
                'category': electronics,
                'name': 'USB-C Charger',
                'slug': 'usb-c-charger',
                'description': 'Fast charging USB-C power adapter',
                'price': '29.99',
                'inventory': 100,
            },
            {
                'category': clothing,
                'name': 'Cotton T-Shirt',
                'slug': 'cotton-tshirt',
                'description': '100% organic cotton comfortable t-shirt',
                'price': '19.99',
                'inventory': 150,
            },
            {
                'category': clothing,
                'name': 'Denim Jeans',
                'slug': 'denim-jeans',
                'description': 'Classic blue denim jeans, comfortable fit',
                'price': '49.99',
                'inventory': 80,
            },
            {
                'category': books,
                'name': 'Python Programming',
                'slug': 'python-programming',
                'description': 'Learn Python from basics to advanced concepts',
                'price': '39.99',
                'inventory': 30,
            },
            {
                'category': books,
                'name': 'Django Web Development',
                'slug': 'django-web-development',
                'description': 'Build modern web apps with Django framework',
                'price': '44.99',
                'inventory': 25,
            },
        ]

        for data in products_data:
            product, created = Product.objects.get_or_create(
                slug=data['slug'],
                defaults=data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created product: {product.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Product already exists: {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample data seeding completed!')
        )
