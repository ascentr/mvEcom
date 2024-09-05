from django.shortcuts import render , get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.template.defaultfilters import slugify
from django.http import HttpResponse , JsonResponse
from django.db import IntegrityError
from accounts.models import UserProfile
from .models import Vendor , OpeningHour
from menu.models import Category , Product  
from accounts.forms import UserProfileForm
from .forms import VendorForm , OpeningHoursForm
from menu.forms import CategoryForm , ProductForm
from accounts.views import check_role_vendor


def get_vendor(request):
    # Helper Function to fetch vendor for the logged in user

    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def vendorProfile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES,   instance=vendor)

        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings Saved')
            return redirect('vendor:vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
        
    context = {
        'profile': profile,
        'vendor':vendor ,
        'profile_form':profile_form ,
        'vendor_form':vendor_form ,
    }

    return render(request, 'vendor/vprofile.html' , context)

@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')

    context = {
        'categories': categories
    }

    return render(request, 'vendor/menu-builder.html' , context)

@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def products_by_category(request,pk=None):
    vendor = get_vendor(request)
    category = Category.objects.get(pk=pk)
    products = Product.objects.filter(vendor=vendor, category=category)

    context = {
        'category' : category,
        'products' : products
    }

    return render(request, 'vendor/products-by-category.html', context)

 #====================================Category Views , Move to Menu App in V2 =============================

@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def add_category(request):

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor=get_vendor(request)
            # category.save()   

            category.slug = slugify(category_name)+'-'+str(category.vendor.id)
            category.save()
            messages.success(request, "Category Added successfully")
            return redirect("vendor:menu-builder")
        else:
            print(form.errors)
    else:
        form = CategoryForm()

    context = { 'form': form   }
    return render(request, 'vendor/add-category.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):

    category = get_object_or_404(Category, pk=pk)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            print("first rint ==>", category_name)
            category = form.save(commit=False)
            category.vendor=get_vendor(request)
            category.slug = slugify(category_name)+'-'+str(category.id)
            print(category.slug)
            category.save()
            messages.success(request, "Category Updated Successfully")
            return redirect("vendor:menu-builder")
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)

    context = { 
        'form': form , 
        'cat' : category,
        }

    return render(request, 'vendor/edit-category.html' , context)


@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category Deleted")

    return redirect('vendor:menu-builder')

 #====================================Product Views , Move to Menu App in V2 =============================

@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST , request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            product = form.save(commit=False)
            print("commit false saved")
            product.vendor = get_vendor(request)
            product.slug = slugify(product.title)
            form.save()

            messages.success(request , 'Product create successfully')
            return redirect('vendor:products-by-category', product.category.id )
        else:
            print(form.errors)
    else:
        form = ProductForm()
        # Modify the form to only show vendor sepecific categories
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = { 'form' : form ,}
    return render(request, 'vendor/add-product.html' , context)

@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def edit_product(request , pk=None):

    product = get_object_or_404(Product,pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES,  instance=product)
        if form.is_valid():
            title = form.cleaned_data['title']
            product = form.save(commit=False)
            product.vendor = get_vendor(request)
            product.slug = slugify(product.title)
            product.save()
            messages.success(request, "Product Updated Successfully")
            return redirect("vendor:products-by-category", product.category.id )
        else:
            print(form.errors)
    else:
        form = ProductForm(instance=product)
        # Modify the form to only show vendor sepecific categories
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = { 
        'form' : form ,
        'product' : product,
        }

    return render(request, 'vendor/edit-product.html' , context )


@login_required(login_url='accounts:login')
@user_passes_test(check_role_vendor)
def delete_product(request, pk=None):
    product = get_object_or_404(Product, pk=pk)
    cat_id = product.category.id
    product.delete()
    print('category is ', cat_id)
    messages.success(request, "Product Deleted")

    return redirect('vendor:products-by-category', product.category.id)


def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=get_vendor(request))
    form = OpeningHoursForm()
    context = {
        'form' : form ,
        'opening_hours':opening_hours,
    }
    return render(request, 'vendor/opening-hours.html',  context)


def add_opening_hours(request):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            # data = [day , from_hour, to_hour, is_closed]
            # print(day , from_hour, to_hour, is_closed)
        
            try:
                hour =OpeningHour.objects.create(vendor=get_vendor(request), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed: 
                        response = { 'status' : 'success' , 'id':hour.id, 'day':day.get_day_display(), 'is_closed' : 'closed' }
                    else:
                        response = {'status' : 'success' , 'id':hour.id, 'day':day.get_day_display() , 'from_hour':hour.from_hour, 'to_hour':hour.to_hour }
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status' : 'fail' , 'message': from_hour+" - "+to_hour+" already exists for this day" }
                return JsonResponse(response)        
        else:
            return HttpResponse("Invalid Request")

def delete_opening_hours(request , pk=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({ 'status': 'success', 'id': pk })





# def delete_opening_hours(request , pk=None):
#     if request.user.is_authenticated:
#         hour = get_object_or_404(OpeningHour, pk=pk)
#         hour.delete()
#         messages.success(request, "Hours Deleted")
#     else:
#         return JsonResponse({'status':'Failed', 'message':'Object does not exist'})
    
#     return redirect('vendor:opening-hours')



