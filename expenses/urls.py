from django.urls import path
from . import views

app_name = 'expenses'
urlpatterns = [
    path('', views.record_list, name='record_list'),
    path('record/new/', views.record_new, name='record_new'),
    path('record/<int:pk>/edit/', views.record_edit, name='record_edit'),
    path('record/<pk>/remove/', views.record_remove, name='record_remove'),
    path('category/list/', views.category_list, name='category_list'),
    path('category/new/', views.category_new, name='category_new'),
    path('category/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('payment/list/', views.payment_list, name='payment_list'),
    path('payment/new/', views.payment_new, name='payment_new'),
    path('payment/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('import/', views.RecordImport.as_view(), name='import'),
    path('export/', views.record_export, name='export'),
]
