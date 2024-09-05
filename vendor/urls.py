from django.urls import path , include
from . import views
from accounts import views as acc_views

app_name = 'vendor'
urlpatterns = [
    path('', acc_views.vendorDashboard, name='vendor'),
    path('profile/' , views.vendorProfile, name='vprofile'),
    path('menu-builder/', views.menu_builder, name='menu-builder'),
    path('menu-builder/category/<int:pk>/', views.products_by_category, name="products-by-category"),
    path('menu-builder/category/add/', views.add_category, name="add-category"),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name="edit-category"),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name="delete-category"),
    path('menu-builder/products/add', views.add_product, name='add-product'),
    path('menu-builder/products/edit/<int:pk>', views.edit_product, name='edit-product'),
    path('menu-builder/products/delete/<int:pk>', views.delete_product, name='delete-product'),
    path('opening-hours/', views.opening_hours, name='opening-hours') ,
    path('opening-hours/add/', views.add_opening_hours, name='add-opening-hours') ,
    path('opening-hours/delete/<int:pk>', views.delete_opening_hours, name='delete-opening-hours') ,
]
