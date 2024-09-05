from menu.models import Product
from .models import Cart , Tax

def get_cart_counter(request):
	cart_count = 0
	if request.user.is_authenticated:
		try:
			cart_items = Cart.objects.filter(user=request.user)
			if cart_items:
				for item in cart_items:
					cart_count += item.quantity
			else:
				cart_count = 0
		except:
			cart_count = 0
	return dict(cart_count=cart_count)


def get_cart_amounts(request):
	subtotal = 0
	tax = 0
	grandtotal = 0
	tax_dict = {}

	if request.user.is_authenticated:
		cart_items = Cart.objects.filter(user=request.user)

		for item in cart_items:
			product = Product.objects.get(pk=item.product.id)
			subtotal += (product.price * item.quantity)

		tax = Tax.objects.get(is_active=True)
		tax_amount = round((tax.tax_percentage * subtotal) / 100 , 2)

		tax_dict.update({ tax.tax_type : { str(tax.tax_percentage): tax_amount  }})

		tax = sum(x for key in tax_dict.values() for x in key.values())
		grandtotal = subtotal + tax

	return dict(subtotal=subtotal,  tax_dict=tax_dict,  tax=tax,  grandtotal=grandtotal )
