from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import json
import datetime

from .models import *
from .utils import *
from .forms import *


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            
            login(request,user)
            return redirect('/')
        else:
            error_message = 'Invalid username or password'
            return render(request,'store/login.html',{'error_message':error_message})
    else:
        return render(request,'store/login.html')

def user_logout(request):
    logout(request)
    return redirect('/')

def user_register(request):
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = 0
            if 'email' in form.changed_data:
                print(form.cleaned_data['email'])
                email = form.cleaned_data['email']
                print(f'email:{email}')

            form.save()           
            user = User.objects.get(username=form.cleaned_data['username'])  
            user.email = email 
            user.save()
            customer= Customer(
                user = user,
                email = form.cleaned_data['email'],
                name = form.cleaned_data['username'],
            )
            customer.save()                     
            
            return redirect('store:login')
            
    else:
        form = UserRegisterForm()                
    return render(request,'store/user_register.html',{'form':form})

def store (request):    
    data = cartData(request)
    cartItem = data['cartItem']          

    products = Product.objects.all()
    context={"products":products,"cartItem":cartItem}
    return render(request,'store/store.html',context)

def cart(request):

    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']     
        
    context={"items":items,"order":order,"cartItem":cartItem}
    return render(request,'store/cart.html',context)

def checkout(request):
    data = cartData(request)
    cartItem = data['cartItem']
    order = data['order']
    items = data['items']  
    u_emails=[]
    emails = User.objects.values_list('email',flat=True)
    
    for email in emails:
        if email != '':
            
            u_emails.append(email)
    
        
    context={"items":items,"order":order,"cartItem":cartItem,"u_emails": json.dumps(u_emails)}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']    

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer,complete=False)

    orderitem, created = OrderItem.objects.get_or_create(order=order,product=product)

    if action == 'add':
        orderitem.quantity = (orderitem.quantity+1)
    elif action == 'remove':
        orderitem.quantity = (orderitem.quantity-1)

    orderitem.save()

    if orderitem.quantity <=0:
        orderitem.delete()

    return JsonResponse('Item was added.', safe=False)

def processOrder(request):
    
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
 

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
            
        
    else:
        customer, order = guestOrder(request,data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()       

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zipcode'],
        )

    return JsonResponse('Payment Completed!',safe=False)
    
   