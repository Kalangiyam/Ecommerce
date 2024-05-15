from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime

from .models import *



# Create your views here.
def store (request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}
        cartItem = order['get_cart_items']
    products = Product.objects.all()
    context={"products":products,"cartItem":cartItem}
    return render(request,'store/store.html',context)

def cart(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items        
    else:  
        items=[]
        order={'get_cart_total':0,'get_cart_items':0,'shipping':False}
        cartItem = order['get_cart_items']
        
    context={"items":items,"order":order,"cartItem":cartItem}
    return render(request,'store/cart.html',context)

def checkout(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItem = order.get_cart_items
        
    else:
        try:
            cart = json.loads(request.COOKIES['cart'])
        except:
            cart = {}

        # print('Cart:',cart)
        items = []
        order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}

        for i in cart:    
            try:        
                product = Product.objects.get(id=i)          
                total = (product.price * cart[i]['quantity'])
                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'price':product.price,
                        'imageURL':product.imageURL,
                    },
                    'get_total':total,
                    'quantity':cart[i]['quantity'],
                }

                items.append(item)

                if product.digital == False:
                    order['shipping']=True
            except:
                pass     

        cartItem = order['get_cart_items']
    context={"items":items,"order":order,"cartItem":cartItem}
    return render(request,'store/checkout.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print(productId)
    print(action)

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
    # else:
        # customer, order = guestOrder(request,data)
        
    order.transaction_id = transaction_id
    total = float(data['form']['total'])
    if total == float(order.get_cart_total):
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
    else:
        print('User is not logged in')
    
    return JsonResponse('Payment Completed!',safe=False)