from django.shortcuts import redirect, render, get_object_or_404  
from django.http import HttpResponse , JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date , datetime
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D  # for Distance
from django.contrib.gis.db.models.functions import Distance
from django.core.exceptions import ObjectDoesNotExist

from vendor.models import Vendor , OpeningHour
from menu.models import Category , Product
from .models import Cart
from orders.forms import OrderForm
from accounts.models import UserProfile
from .context_processors import get_cart_counter, get_cart_amounts


def marketplace(request):
	vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
	vendro_count = vendors.count()
	context = {'vendors' : vendors , 'vendro_count':vendro_count }

	return render(request, 'marketplace/marketplace.html' , context )


def vendor_detail(request, vendor_slug):
	vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
	categories = Category.objects.filter(vendor=vendor).prefetch_related(
		Prefetch('products' , queryset= Product.objects.filter(is_available=True)))
	
	opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')
	today = date.today().isoweekday()
	hours_today = OpeningHour.objects.filter(vendor=vendor, day=today ).order_by('from_hour')

	if request.user.is_authenticated:
		cart_items = Cart.objects.filter(user=request.user)
	else:
		cart_items = None

	context = { 
		'vendor':vendor , 
		'categories' : categories ,
		'cartItems' : cart_items,
		'opening_hours': opening_hours ,
		'hours_today' : hours_today ,
		}
	
	return render(request, 'marketplace/vendor-detail.html' , context)


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if product exists
            try:
                product = Product.objects.get(id=product_id)
                # Check if product already in cart
                try:
                    check_cart = Cart.objects.get(user=request.user, product=product)
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Cart Quantity Increased', 
	                    		'cart_counter':get_cart_counter(request), 
	                    		'itemQty' : check_cart.quantity  ,
	                    		'cart_amount' : get_cart_amounts(request) 
	                    		})
                except Cart.DoesNotExist:
                    check_cart = Cart.objects.create(user=request.user, product=product, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Product Added to cart', 
	                    		'cart_counter':get_cart_counter(request),  
	                    		'itemQty' : check_cart.quantity ,
	                    		'cart_amount' : get_cart_amounts(request) 
	                    	})
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Product Does not exist'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request'})
    else:
    	return JsonResponse({'status':'login_required', 'message':'Please Login to continue'})


def remove_cart_item(request, product_id):
	if request.user.is_authenticated:
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			try:
				product = Product.objects.get(id=product_id)
				try:
					check_cart = Cart.objects.get(user=request.user, product=product)
					if check_cart.quantity > 1:
						check_cart.quantity -= 1
						check_cart.save()
					else:
						check_cart.delete()
						check_cart.quantity = 0
					return JsonResponse({'status' : 'Success', 
							'cart_counter': get_cart_counter(request), 
							'itemQty' : check_cart.quantity ,
							'cart_amount' : get_cart_amounts(request)  
						})
				except Cart.DoesNotExist:
					return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart !'  })

			except Product.DoesNotExist:
				return JsonResponse({'status': 'Failed', 'message': 'Product Does not exist'})
		else:
			return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})
	else:
		return JsonResponse({'status': 'login_required', 'message': 'Please Login to continue'})

@login_required(login_url='accounts:login')
def cart(request):
	cart_items = Cart.objects.filter(user=request.user).order_by('product')
	context = { 'cart_items':cart_items }

	return render(request, 'marketplace/cart.html' , context)


def delete_cart_item(request, cart_id):
	if request.user.is_authenticated:
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			try:
				cart_item = Cart.objects.get(user=request.user, id=cart_id)
				if cart_item:
					cart_item.delete()
					return JsonResponse({ 'status' : 'Success', 'message': 'Item Deleted', 
						'cart_counter':get_cart_counter(request), 'cart_amount' : get_cart_amounts(request)   
						})

			except Cart.DoesNotExist:
				return JsonResponse({'status': 'Failed', 'message': 'No Cart Item'  })
		else:
			return JsonResponse({'status': 'Failed', 'message': 'Invalid Request'})


def search(request):
	if not 'address' in request.GET:
		return redirect ('marketplace')
	else:
		address = request.GET['address']
		latitude = request.GET['latitude']
		longitude = request.GET['longitude']
		radius = request.GET['radius']
		keyword = request.GET['keyword']

		#get vendors by food search
		fetch_vendors_by_product = Product.objects.filter(title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
		vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_product) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True))
		
		# vendors within a location radius
		if latitude and longitude and radius:
			pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))

			vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_product) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True), 
				user_profile__location__distance_lte=(pnt, D(km=radius))).annotate(distance=Distance("user_profile__location" , pnt )).order_by("distance")
			
			for v in vendors:
				v.kms = round(v.distance.km, 1)

		#vendors = Vendor.objects.filter(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)
		vendors_count = vendors.count()
		context = { 
			'vendors' : vendors , 
			'vendors_count': vendors_count, 
			'source_location': address ,
		}
		
		return render (request, 'marketplace/listings.html' , context)
	
@login_required(login_url='accounts:login')
def checkout(request):
	cart_items = Cart.objects.filter(user=request.user)
	cart_count = cart_items.count()
	if cart_count <= 0:
		return redirect("marketplace")

	user_profile = UserProfile.objects.get(user=request.user)

#pre-populate the user form
	default_values = {
		'first_name':request.user.first_name ,
		'last_name' : request.user.last_name ,
		'phone':request.user.phone_number,
		'email':request.user.email,
		'address':user_profile.address,
		'country':user_profile.country,
		'state': user_profile.state,
		'city': user_profile.city,
		'post_code':user_profile.postcode
	}

	form = OrderForm(initial=default_values)
	context = { 
		'form' : form, 
	    'cart_items' : cart_items ,
		}

	return render(request, 'marketplace/checkout.html' , context)

