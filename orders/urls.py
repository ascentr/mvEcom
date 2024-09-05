from django.urls import path, include
from . import views

app_name = 'orders'

urlpatterns = [
    path('place-order/', views.place_order, name="place-order"),
    path('payments/', views.payments, name="payments"),
    path('order-complete/', views.order_complete, name='order-complete')
    # path('', views.orders, name="orders"),
]