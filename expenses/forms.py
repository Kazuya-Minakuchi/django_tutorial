from django import forms

from .models import Record, Category, Payment

class RecordForm(forms.ModelForm):

    class Meta:
        model = Record
        fields = ('expense_date', 'amount', 'category', 'payment', 'note')

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name',)

class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ('name',)
