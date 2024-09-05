from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from vendor.forms import VendorForm
from .models import User , UserProfile
from django.contrib import messages

def registerUser(request):
    if request.method=='POST':
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, "Account Created Successfully")
            return redirect('accounts:registeruser')
        else:
            print(form.errors)

    else:
        form = UserForm()

    context =  {'form' :  form }
    return render(request, 'accounts/registerUser.html',  context)


def registerVendor(request):
    if request.method=='POST':
        u_form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)

        if u_form.is_valid() and v_form.is_valid():
            first_name = u_form.cleaned_data['first_name']
            last_name =  u_form.cleaned_data['last_name']
            email =      u_form.cleaned_data['email']
            username =   u_form.cleaned_data['username']
            password =   u_form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name , last_name=last_name,
                email=email, username=username, password=password)
            user.role = user.VENDOR
            user.save()

            vendor = v_form.save(commit=False)
            vendor.user = user
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, "Account Registered, Please wait for approval")
            return redirect('accounts:registervendor')

        else:
            print("Invalid Form" , u_form.errors, v_form.errors)
    else:
        u_form = UserForm()
        v_form = VendorForm()

    context = {
        'u_form' : u_form ,
        'v_form' : v_form
    }
    return render(request, 'accounts/registerVendor.html',  context)

# register user using create_user Method defined in models:
# def registerUser(request):
#     if request.method=='POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             first_name = form.cleaned_data['first_name']
#             last_name = form.cleaned_data['last_name']
#             email = form.cleaned_data['email']
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#
#             user=User.objects.create_user(first_name=first_name , last_name=last_name,
#                 email=email, username=username, password=password)
#
#             user.role=User.CUSTOMER
#             user.save()
#             return redirect('registeruser')
#         else:
#             print(form.errors)
#     else:
#         form = UserForm()
#
#     context = {'form': form}
#
#     return render(request, 'accounts/registerUser.html', context)
