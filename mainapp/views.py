from django.shortcuts import render, HttpResponse, redirect
from .models import *
from .models import Expiry
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
import random
from twilio.rest import Client
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
    
def signup(request):
    if request.method=='POST':
        username=request.POST.get('username')
        phonenumber=request.POST.get('phonenumber')
        password=request.POST.get('password')
        location = request.POST.get('location') == 'on'
        print(location)
        print(type(location))
        if CustomUser.objects.filter(phonenumber=phonenumber).exists() or CustomUser.objects.filter(username=username).exists():
            showerror=True
            return render(request, 'signup.html', context={'error':showerror})
        user = CustomUser.objects.create_user(username=username, phonenumber=phonenumber, password=password, location=location)
        user.save()
        return redirect('login')
    return render(request, 'signup.html')



def getphonenumber(request):
    if request.method == 'POST':
        phonenumber=request.POST.get('phonenumber')
        if not CustomUser.objects.filter(phonenumber=phonenumber).exists():
            showerror=True
            return render(request, 'enterphonenumber.html', context={'error':showerror})
        twilionumber='+81'+phonenumber[1:]
        otp=random.randint(100000, 999999)

        account_sid = 'AC4a4162cbb61436f7b36897ba1f150655'
        auth_token = '97a1206c35505052d740bd056bf083d4'
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            to='whatsapp:{}'.format(twilionumber),
            body='your reset password otp is {}'.format(otp),
        )
        request.session['otp'] = int(otp)
        request.session['phonenumber'] = phonenumber
        return render(request, 'enterotp.html')
    else:
        return render(request, 'enterphonenumber.html')
    
def getotp(request):
    if request.method == 'POST':
        otp = request.session.get('otp')
        receivedotp = int(request.POST.get('otp'))
        if otp==receivedotp:
            return render(request, 'enternewpassword.html')
        else:
            showerror=True
            return render(request, 'enterotp.html', context={'error':showerror})
    else:
        return(request, 'enterotp.html')

def getpassword(request):
    if request.method == 'POST':
        phonenumber=request.session.get('phonenumber')
        user=CustomUser.objects.filter(phonenumber=phonenumber).first()
        user.set_password(request.POST.get('password'))
        user.save()
        return redirect('login')

from datetime import datetime
from django.utils import timezone


@login_required
def showproduct(request):
    if request.method == 'POST':
        varbutton='Add to Cart'
        getitem = request.POST.get('item_id')
        defquan=False
        if request.POST.get('itemid'):
            useritemid=request.POST.get('itemid')
            useritem=UserItem.objects.get(id=useritemid)
            getitem=useritem.item.id
            defquan=int(request.POST.get('defquan'))
            varbutton='Confirm new Quantity'
        showitem = Item.objects.get(id=getitem)
        categories = showitem.categories.all()  # Fetch all related categories for the item
        relateditems = Item.objects.filter(categories__in=categories).exclude(id=showitem.id).distinct()
        if len(relateditems)==0:
            relateditems=False
        context={
            'showitem':showitem,
            'varbutton':varbutton,
            'relateditems':relateditems,
            'defquan':defquan
        }
        return render(request, 'showproduct.html', context)
    
def homepage(request):
    items = Item.objects.all()
    allexpiry=Expiry.objects.all()
    # delete expired expiries #
    for expiry in allexpiry:
        #print(expiry.quantity)
        if expiry.date<timezone.now():
            expiry.delete()
    # delete expired expiries #

    # Update item quantity #
    for item in items:
        expiries=Expiry.objects.filter(item=item)
        """
        for x in expiries:
            print("quantity {}".format(x.quantity))
        """
        totalquantity=sum([x.quantity for x in expiries])
        item.availablequantity=totalquantity
        item.save()
    # Update item quantity #

    if not request.user.is_authenticated:
        return redirect('login')

    # Get announcements
    announcements = Category.objects.filter(announcement=True)
    announcementlist=[]
    announcementname=[]
    for ann in announcements:
        appendlist=[item for item in ann.items.all() if item.availablequantity>0]
        if len(appendlist)>0:
            announcementname.append(ann.name)
            announcementlist.append(appendlist)
    announcementlist=zip(announcementlist, announcementname)
    categories = Category.objects.all()
    context = {
        'items': items,
        'categories': categories,
        'noquantity': False,
        'announcements': announcementlist,
        'isfilter': False,
        'catname': False,
    }
    return render(request, 'homepage.html', context)

def products(request):
    #receive filter
    catitems=False
    searchnoquan=False
    filcatname=False
    matching_items=False
    if request.method == 'POST':
        if request.POST.get('handlesearch'):
            receivedsearch = request.POST.get('handlesearch')
            if receivedsearch:
                matching_items = Item.objects.filter(
                    Q(name__icontains=receivedsearch) | Q(description__icontains=receivedsearch))
            if len(matching_items)==0:
                searchnoquan=True

        else:
            getcat = request.POST.get('category')
            if getcat=="allitems":
                return redirect('products')
            showcategory=Category.objects.get(id=getcat)
            filcatname=showcategory.name
            catitems=Item.objects.filter(categories=showcategory)
            for item in catitems:
                if item.availablequantity!=0:
                    noquantity=False
                    break
                else:
                    noquantity=True
    else:
        catitems=False
        filcatname=False
        matching_items=False

    items = Item.objects.all()
    allexpiry=Expiry.objects.all()
    # delete expired expiries #
    for expiry in allexpiry:
        #print(expiry.quantity)
        if expiry.date<timezone.now():
            expiry.delete()
    # delete expired expiries #

    # Update item quantity #
    for item in items:
        expiries=Expiry.objects.filter(item=item)
        """
        for x in expiries:
            print("quantity {}".format(x.quantity))
        """
        totalquantity=sum([x.quantity for x in expiries])
        item.availablequantity=totalquantity
        item.save()
    # Update item quantity #

    if not request.user.is_authenticated:
        return redirect('login')

    # Get announcements
    announcements = Category.objects.filter(announcement=True)
    announcementlist=[]
    announcementname=[]
    for ann in announcements:
        appendlist=[item for item in ann.items.all() if item.availablequantity>0]
        if len(appendlist)>0:
            announcementname.append(ann.name)
            announcementlist.append(appendlist)
    announcementlist=zip(announcementlist, announcementname)
    categories = Category.objects.all()
    context = {
        'catitems':catitems,
        'searchnoquan':searchnoquan,
        'matchingitems':matching_items,
        'filcatname':filcatname,
        'items': items,
        'categories': categories,
        'announcements': announcementlist,
        'isfilter': False,
        'catname': False,
    }
    return render(request, 'products.html', context)


@login_required
def addtocart(request):
    if request.method == 'POST':
        item = Item.objects.get(id=request.POST.get('item_id'))
        quantity = int(request.POST.get('quantity', 1))

        if request.POST.get('editquan'):
            useritem=UserItem.objects.filter(user=request.user, item=item).first()
            useritem.quantity=quantity
            useritem.save()
            return redirect('cart')
        else:
            checker=UserItem.objects.filter(user=request.user, item=item).exists()
            if checker:
                useritem=UserItem.objects.filter(user=request.user, item=item).first()
                if quantity+useritem.quantity<useritem.item.availablequantity:
                    useritem.quantity+=quantity
                else:
                    useritem.quantity=useritem.item.availablequantity
                useritem.save()
            else:
                user_item, created = UserItem.objects.get_or_create(user=request.user, item=item)
                user_item.quantity = quantity
                user_item.save()

        return HttpResponse(status=204)
        


@login_required
def cart(request):
    user_items = UserItem.objects.filter(user=request.user)
    price_list=[x.item.price*x.quantity for x in user_items]
    totalprice=sum(price_list)
    if request.session.get('submitcamefirst'):
        error=bool(request.session.get('minorder'))
    else:
        error=False
    request.session['submitcamefirst']=False
    if request.user.location==True:
        minprice=9000
    else:
        minprice=5000
    context = {
        'user_items': zip(user_items, price_list),
        'error': error,
        'minprice':minprice,
        'carttotal':totalprice 
    }
    request.session['minorder'] = False
    return render(request, 'cart.html', context)

def deleteitem(request):
    if request.method == 'POST':
        item_id = request.POST.get('deleteitem')
        user = request.user
        item = get_object_or_404(Item, id=item_id)
        user_item = get_object_or_404(UserItem, user=user, item=item)
        item.users.remove(user)
        user_item.delete()
        return redirect('cart')
    return redirect('cart')

def history(request):
    items= reversed(userhistory.objects.filter(user=request.user))
    context={
        'items': items
    }
    return render(request, 'history.html', context)

def account(request):
    return render(request, 'account.html')

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Q

def logoutuser(request):
    logout(request)
    return redirect('login')

from django.views import View
class ProductAutocomplete(View):
    def get(self, request):
        query = request.GET.get('term', '')
        products = Item.objects.filter(name__icontains=query)[:10]
        results = [product.name for product in products]
        return JsonResponse(results, safe=False)
    
def handlesearch(request):
    if request.method == 'POST':
        receivedsearch = request.POST.get('handlesearch')
        if receivedsearch:
            matching_items = Item.objects.filter(
                Q(name__icontains=receivedsearch) | Q(description__icontains=receivedsearch))

            for item in matching_items:
                if item.availablequantity!=0:
                    noquantity=False
                    break
                else:
                    noquantity=True
                    
            Categories=Category.objects.all()
            context={
            'items':matching_items,
            'categories':Categories,
            'noquantity':noquantity,
            'isfilter':False,
            'catname':False,
            }
            return render(request, 'homepage.html', context)
    return render(request, 'homepage.html', {'items': Item.objects.all()})


#########################################
#########################################
#########################################
import stripe
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
stripe.api_key = settings.STRIPE_SECRET_KEY
def paymentsuccess(request):
     
    message="Order Received-\n"
    totalprice=0

    user_items = UserItem.objects.filter(user=request.user)
    for useritem in user_items:
        user=request.user
        name=useritem.item.name 
        quantity=useritem.quantity 
        price=useritem.quantity*useritem.item.price
        totalprice+=price
        message+="Item->{} === Qty->{} === Total->{}\n".format(name, quantity, price)

        userhistoryobj=userhistory.objects.create(user=user, 
                                                name=name, 
                                                quantity=quantity, 
                                                totalprice=price)
        userhistoryobj.save()
        mainitem=useritem.item
        # decrease quantity of item #
        itemexpiries=mainitem.expiry.all()
        expirydates=[x.date for x in itemexpiries]
        sortedexpiries=sorted(expirydates, reverse=False)
        expiriesinorder=[]
        for date in sortedexpiries:
            expiry=(Expiry.objects.filter(item=mainitem, date=date)).first()
            expiriesinorder.append(expiry)
        for expiry in expiriesinorder:
            if expiry.quantity>quantity:
                expiry.quantity-=quantity
                expiry.save()
                break
            else:
                quantity-=expiry.quantity
                expiry.delete()
        # decrease quantity of item #
        mainitem.save()
        useritem.delete()
    

    message+="Total Bill-> {}\n the order type is--> {}\n Phonenumber--> {}".format(totalprice, request.session.get('ordertype'), request.user.phonenumber)

    account_sid = 'AC4a4162cbb61436f7b36897ba1f150655'
    auth_token = '97a1206c35505052d740bd056bf083d4' 
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=message,
    to='whatsapp:+818035063523'
    )
    
    items= reversed(userhistory.objects.filter(user=request.user))
    context={
        'items': items,
        'ordermessage':True
    }
    return render(request, 'history.html', context)

stripe.api_key = settings.STRIPE_SECRET_KEY

def submitorder(request):
    request.session['minorder'] = True
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user_items = UserItem.objects.filter(user=request.user)
        if len(user_items)==0:
            return redirect('cart')
        ordertype=str(request.POST.get('ordertype'))
        totalprice=0
        for useritem in user_items:
                price=useritem.quantity*useritem.item.price
                totalprice+=price
        
        if request.user.location==True and ordertype=='Home Delivery':
            if totalprice<=9000:
                request.session['minorder'] = True
                request.session['submitcamefirst']=True
                return redirect('cart')
        elif request.user.location==False and ordertype=='Home Delivery':
            if totalprice<=5000:
                request.session['minorder'] = True
                request.session['submitcamefirst']=True
                return redirect('cart')
        request.session['ordertype'] = ordertype

        session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'jpy',
                'product_data': {
                    'name': 'Final Billing', 
                },
                'unit_amount': int(totalprice),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/paymentsuccess',  
        cancel_url='http://127.0.0.1:8000/cart',   
    )
    
    context = {
        'total_price': totalprice,
        'session_id': session.id,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, 'payment_template.html', context)

def loginview(request):
    if request.method=='POST':
        phonenumber=request.POST.get('phonenumber')
        password=request.POST.get('password')
        user = authenticate(request, phonenumber=phonenumber, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            showerror=True
            return render(request, 'login.html', context={'error':showerror})
    return render(request, 'login.html')