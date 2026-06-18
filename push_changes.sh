#!/bin/bash
cd "F:\Documents\Projects Worked On\Python"
git add store/views.py store/customer_forms.py store/templates/store/login.html store/templates/store/register.html store/templates/store/order_history.html store/templates/store/order_detail.html store/templates/store/password_reset.html store/urls.py requirements.txt .github/workflows/tests.yml
git commit -m "Add customer authentication and order management features"
git push origin main
