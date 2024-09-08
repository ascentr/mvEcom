from django.urls import path
from accounts import views as accViews
from . import views

app_name = 'customers'

urlpatterns = [
    path('', accViews.customerDashboard, name="customer"),
    path('profile/' , views.customer_profile, name="cprofile"),
    path('myorders/', views.my_orders, name='cust-myorders'),
    path('order-detail/<int:pk>', views.order_detail, name='order-detail'),
]