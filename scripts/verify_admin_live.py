import urllib.request
import sys
url = 'http://127.0.0.1:8090/admin/'
try:
    resp = urllib.request.urlopen(url)
    html = resp.read().decode('utf-8')
    print('STATUS', resp.getcode())
    print('HAS_CSS', '/static/store/admin.css' in html)
    print('HAS_VIEWSITE', 'class="view-site"' in html)
    # print a snippet around <head>
    i = html.find('<head')
    if i!=-1:
        print(html[i:i+800])
except Exception as e:
    print('ERROR', e)
    sys.exit(2)
