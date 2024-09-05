from django.urls import path
from . import views

# app_name = 'marketplace'

urlpatterns = [
	path('', views.marketplace, name='marketplace'),
	path('cart/', views.cart, name='cart'),
	path('<slug:vendor_slug>/' , views.vendor_detail, name="vendor-detail"), 
	path('add-to-cart/<int:product_id>', views.add_to_cart, name="add-to-cart"),
	path('remove-cart-item/<int:product_id>', views.remove_cart_item, name="remove-cart-item"),
	path('delete-cart-item/<int:cart_id>', views.delete_cart_item, name="delete-cart-item"),

]