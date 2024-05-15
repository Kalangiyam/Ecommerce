import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

        
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
    return {"items":items,"order":order,"cartItem":cartItem}