import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','store_api.settings')
import django
django.setup()
from django.test import Client
c = Client()
r = c.get('/admin/', follow=True)
print('FINAL_STATUS', r.status_code)
text = r.content.decode('utf-8')
print('HAS_CSS', 'store/admin.css' in text)
print('HAS_VIEWSITE', 'class="view-site"' in text)
# Optional: print snippet
start = text.find('<head')
print(text[start:start+800])
