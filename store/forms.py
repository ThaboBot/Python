from django import forms


class OrderForm(forms.Form):
    customer_name = forms.CharField(max_length=200, label='Your name')
    customer_email = forms.EmailField(label='Your email')
    quantity = forms.IntegerField(min_value=1, initial=1, label='Quantity')
