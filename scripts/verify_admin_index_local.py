import os, sys
sys.path.insert(0, r'F:/Documents/Projects Worked On/Python')
os.environ.setdefault('DJANGO_SETTINGS_MODULE','store_api.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()

c = Client()
# use known superuser credentials; change if different
username = 'admin'
password = 'AdminPass123!'
# login via client
logged = c.login(username=username, password=password)
print('LOGGED_IN', logged)
resp = c.get('/admin/', HTTP_HOST='127.0.0.1')
print('INDEX_STATUS', resp.status_code)
text = resp.content.decode('utf-8')
print('HAS_CSS', '/static/store/admin.css' in text)
print('HAS_VIEWSITE', 'class="view-site"' in text)
# print snippet around branding
i = text.find('site-name')
if i!=-1:
    print(text[i:i+400])
else:
    print(text[:800])
