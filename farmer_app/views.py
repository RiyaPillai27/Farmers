from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login,logout
from .models import product,Cart,Order
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail
# Create your views here.
def about(request):
    return HttpResponse("hello for the about ")
def myprofile(request):
    return HttpResponse("we will add the general information of ourself")
def cart(request):
    return HttpResponse("in here we can add items and order it")
def contact(request):
    return HttpResponse("<h1> hello from contact page</h1>")  
def edit(request,rid):
    return HttpResponse("id to be edited:"+rid)
def addition(request,x1,x2):
    t=int(x1)+int(x2)
    t=str(t)
    return HttpResponse("addition is:"+t)   

def hello(request):
    context={}
    context['greet']=" hello, we are learning DTL "
    context['x']=100
    context['y']=20
    context['l']=[10,20,30,40,50]
    context['student']=[
        {'id':1,'name':'riya','age':24, 'gender':'female' },
        {'id':2,'name':'lavit','age':2, 'gender':'male' },
        {'id':3,'name':'vipin','age':32, 'gender':'male'}
        ]
    return render(request,'hello.html',context)                    

def home(request):
    #userid=request.user.id
    #print("id of logged in user:",userid)
    #print("result:",request.user.is_authenticated)
    p=product.objects.filter(is_active=True)
    print(p)
    context={}
    context['product']=p
    return render(request,'index.html',context)    

def product_detail(request,pid):
    p=product.objects.filter(id=pid)
    print(p)
    context={}
    context['product']=p
    return render(request,'product_detail.html',context)    

def register(request):
    if request.method=='POST':
        uname =request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        context={}
        #print(uname,"-",upass,"-",ucpass)
        if uname=="" or upass=="" or ucpass=="":
            context['errmsg']="Fields can not be Empty"
            return render(request,'register.html',context)
        elif upass != ucpass:
            context['errmsg']="Password & confirm password didn't match"
            return render(request,'register.html',context)
        else:
             try:
                 u=User.objects.create(password=upass,username=uname,email=uname)
                 u.set_password(upass)
                 u.save()
                 context['success']="User created Sucessfully , Please Login"
                 return render(request,'register.html',context)
                 #return HttpResponse("User Created Successfully")
             except Exception:
                 context['errmsg']="User with same username already exist"
                 return render(request,'register.html',context)
    else:
        return render(request,'register.html') 

def user_login(request):
    if request.method=='POST':
        uname=request.POST['uname']
        upass=request.POST['upass']
        #print(uname,"--",upass)
        #return HttpResponse('data is fetched')
        context={}
        if uname=="" or upass=="":
            context['errmsg']="fields can not be empty"
            return render(request,'login.html',context)
        else:
            u=authenticate(username=uname,password=upass)
            #print(u)
            #print(u.username)
            #print(u.is_superuser)
            if u is not None:
                login(request,u)
                return redirect('/home')
            else:
                context['errmsg']="Invalid Username & Password"
                return render(request,'login.html',context)   
    else:
        return render(request,'login.html')
    
def user_logout(request):
    logout(request)
    return redirect('/home')    

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html') 

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1 & q2)
    #print(p)
    context={}
    context['product']=p
    return render(request,'index.html',context)  

def sort(request,sv):
    if sv == '0':
        col='price'
    else:
        col='-price'
    p=product.objects.filter(is_active=True).order_by(col)
    context={}
    context['product']=p
    return render(request,'index.html',context)   

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    #print(min)
    #print(max)
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['product']=p
    return render(request,'index.html',context)
    #return HttpResponse("values fetched") 
     
def addtocart(request,pid):
    if request.user.is_authenticated:
       userid=request.user.id
       #print(pid)
       #print(userid)
       u=User.objects.filter(id=userid)
       #print(u[0])
       p=product.objects.filter(id=pid)
       #print(p[0])
       q1=Q(uid=u[0])
       q2=Q(pid=p[0])
       c=Cart.objects.filter(q1 & q2)
       n=len(c)
       context={}
       context['product']=p
       if n==1:
           context['msg']="product already exits in cart!!"
       else:
           c=Cart.objects.create(uid=u[0],pid=p[0])
           c.save()
           context['success']="product added successfully to cart!!"
       return render(request,'product_detail.html',context)
       #return HttpResponse("Product added to cart ")
    else:
        return redirect('/login')                     
    
def viewcart(request):
    c=Cart.objects.filter(uid=request.user.id)
    #print(c)
    #print(c[0].uid)
    #print(c[0].pid)
    #print(c[0].pid.price)
    #print(c[0].uid.is_superuser)
    s=0
    np=len(c)
    for x in c:
        s= s + x.pid.price*x.qty
    print(s)    
    context={}
    context['data']=c
    context['total']=s
    context['n']=np
    return render(request,'cart.html',context) 

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    orders=Order.objects.filter(id=cid)
    orders.delete()
    return redirect('/viewcart')  

def updateqty(request,qv,cid):
    c=Cart.objects.filter(id=cid)
    print(c)
    print(c[0])
    print(c[0].qty)
    if qv == '1':
        t=c[0].qty+1
        c.update(qty=t) #update operation-cart table
    else:
        if c[0].qty>1:
            t=c[0].qty - 1
            c.update(qty=t)
    #return HttpResponse("quantity")
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    c=Cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    #print(oid)
    for x in c:
        #print(x)
        #print(x.pid)
        #print(x.uid)
        #print(x.qty)
        o=Order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()
        x.delete() #delete records from cart table
    orders=Order.objects.filter(uid=request.user.id)
    context={}
    context['data']=orders
    s=0
    np=len(orders)
    for x in orders:
        s=s+x.pid.price*x.qty
    context['total']=s
    context['n']=np        
    #return HttpResponse("in placeorder")
    return render(request,'placeorder.html',context)

def makepayment(request):
    uemail=request.user.username
    orders=Order.objects.filter(uid=request.user.id)
    s=0
    np=len(orders)
    for x in orders:
        s=s+x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_QXEoOzYC2jsh1p", "uKFUvA41J35ZTBadlLX3MYs9"))
    data = { "amount": s*100, "currency": "INR", "receipt": "oid" }
    payment = client.order.create(data=data)
    #print(payment)
    context={}
    context['data']=payment
    context['uemail']=uemail
    return render(request,'pay.html',context)
     
def sendusermail(request,uemail):
    #print("========",uemail)
    msg="order details"
    send_mail(
        'Ekart -order placed successfully',
        msg,
        'riapillai27@gmail.com',
        [uemail],
        fail_silently=False,
    )
    return HttpResponse("mail send successfully")     