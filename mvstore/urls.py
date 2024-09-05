
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from marketplace import views as mpViews


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home") ,
    path('about/', views.about, name="about") ,
    path('accounts/', include('accounts.urls' ,  namespace="accounts")),
    path('customer/', include('customers.urls', namespace="customer")),
    path('vendor/', include('vendor.urls' ,  namespace="vendor")),
    path('marketplace/', include('marketplace.urls')) ,
    path('checkout/', mpViews.checkout, name="checkout"),
    path('orders/', include('orders.urls')) ,
    path('search/', mpViews.search, name="search" )
    
 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
