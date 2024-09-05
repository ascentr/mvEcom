from django.http import HttpResponse, JsonResponse
from django.shortcuts import render , redirect 
import simplejson as json
from django.contrib.auth.decorators import login_required
from marketplace.models import Cart
from marketplace.context_processors import get_cart_amounts
from .forms import OrderForm
from .models import Order , Payment, OrderedProduct
from .utils import generate_order_number
from accounts.utils import send_notification

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect(request, 'marketplace')
        
    
    subtotal   = get_cart_amounts(request)["subtotal"]
    total_tax  = get_cart_amounts(request)["tax"]
    grandtotal = get_cart_amounts(request)["grandtotal"]
    tax_data   = get_cart_amounts(request)["tax_dict"]

    print(json.dumps(tax_data))

    if request.method=="POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address = form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.post_code = form.cleaned_data['post_code']
            order.user = request.user
            order.total = grandtotal
            order.tax_data = json.dumps(tax_data)
            order.total_tax = total_tax
            order.payment_method = request.POST['payment-method']
            order.save() #generate pk
            order.order_number = generate_order_number(order.id)
            order.save()
            context = {
                'order' : order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place-order.html', context)
        else:
            print(form.errors)

    return render(request, 'orders/place-order.html')


@login_required(login_url='login')
def payments(request):
    #check if ajax request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')
        
        order = Order.objects.get(user=request.user, order_number=order_number)

        #store payment details in payment model    
        payment = Payment(
            user= request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status
        )
        
        payment.save()

        #update order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        #move caret items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_product = OrderedProduct()
            ordered_product.order = order
            ordered_product.payment = payment
            ordered_product.user = request.user
            ordered_product.product = item.product
            ordered_product.quantity = item.quantity
            ordered_product.price = item.product.price
            ordered_product.amount = item.product.price * item.quantity

            ordered_product.save()
            
        #send order confirmation email
        mail_subject = 'Thanks for Ordering'
        mail_template = 'orders/order_confirmation_email.html'
        context = { 
            'user' : request.user,
            'order' : order,
            'to_email' : order.email,
            }
        print("customer email => , to_email=", order.email)
        send_notification(mail_subject, mail_template, context)
    
        #order received email to the vendor
        mail_subject = 'You received a new order'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        for i in cart_items:
            if i.product.vendor.user.email not in to_emails:
                to_emails.append(i.product.vendor.user.email)
        
        print('to_emails =>', to_emails)
        context = {
            'order': order,
            'to_email': to_emails
        }
        send_notification(mail_subject, mail_template, context)

        #if payment successfull clear cart
        response = {
            'order_number':order_number,
            'transaction_id':transaction_id
        }
        # cart_items.delete()
        return JsonResponse(response)

    else:
        print("WTF Happened !!")
    return HttpResponse('Payments View')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_products = OrderedProduct.objects.filter(order=order)

        subtotal = 0
        for item in ordered_products:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)

        context = {
            'order': order ,
            'ordered_products': ordered_products,
            'subtotal' : subtotal,
            'tax_data' : tax_data,
        }

        return render(request, 'orders/order_complete.html', context)
    except:
        return render(request, 'orders/order_complete.html')    

