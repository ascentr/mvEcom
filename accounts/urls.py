from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.myAccount ),
    path('registeruser/', views.registerUser, name='registeruser'),
    path('registervendor/', views.registerVendor, name='registervendor'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('myaccount/', views.myAccount, name='myaccount'),
    path('customerdashboard/', views.customerDashboard, name='customerdashboard'),
    path('vendordashboard/', views.vendorDashboard, name='vendordashboard'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>' , views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/', views.reset_password, name='reset_password'),
]
