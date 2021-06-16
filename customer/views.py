from django.conf.urls import url
from django.conf.urls.static import static
from .models import MenuItem, OrderModel
# from django.http.response import HttpResponse
from django.shortcuts import render,redirect
from django.views import View
from django.core.mail import send_mail
import json
from django.db.models import Q
class Index(View):
    def get(self,request,*args,**kwargs):
        return render(request,'customer/index.html')


class About(View):
    def get(self,request,*args,**kwargs):
        return render(request,'customer/about.html')

class Order(View):

    def get(self, request, *args, **kwargs):
        appetizers = MenuItem.objects.filter(category__name__contains='Appetizer')
        entres = MenuItem.objects.filter(category__name__contains='Entre')
        desserts = MenuItem.objects.filter(category__name__contains='Desert')
        drinks = MenuItem.objects.filter(category__name__contains='Drink')

        context = {
            'appetizers': appetizers,
            'entres': entres,
            'desserts': desserts,
            'drinks': drinks,
        }

        return render(request,'customer/order.html',context)

    def post(self, request, *args, **kwargs):
        name=request.POST.get('name')
        email=request.POST.get('email')
        street=request.POST.get('street')
        city=request.POST.get('city')
        state=request.POST.get('state')
        pin_code=request.POST.get('pin_code')

        order_items={
            'items':[]
        }

        items=request.POST.getlist('items[]')

        for item in items:
            menu_item=MenuItem.objects.get(pk=int(item))
            item_data={
                'id':menu_item.pk,
                'name':menu_item.name,
                'price':menu_item.price
            }

            order_items['items'].append(item_data)  

            price=0

            item_ids=[]

        for item in order_items['items']:
            price+=item['price']
            item_ids.append(item['id'])

        order=OrderModel.objects.create(price=price,name=name,email=email,street=street,city=city,state=state,pin_code=pin_code)
        order.items.add(*item_ids)

        body=('Thank you for your Order ! Your Food is being made and will be delivered Soon!\n'
                f'Your Total:{price}\n'
                'Thank you again for your order!')

        #Confirmation Email
        send_mail(
            'Thank You for Your Order!!',
            body,
            'khaan-paan@khaan-paan.com',
            [email],
            fail_silently=False
        )

        # context={
        #     'items':order_items['items'],
        #     'price':price
        # }

        # return render(request,'customer/order_confirmation.html',context)
        return redirect('order-confirmation',pk=order.pk)

class OrderConfirmation(View):
    def get(self,request,pk,*args,**kwargs):
        order=OrderModel.objects.get(pk=pk)

        context={
            'pk':order.pk,
            'items':order.items,
            'price':order.price
        }

        return render(request,'customer/order_confirmation.html',context)

    def post(self,request,pk,*args,**kwargs):
        data= json.loads(request.body)
        if data['isPaid']:
            order=OrderModel.objects.get(pk=pk)
            order.is_paid=True
            order.save()
        return redirect('payment-confirmation')

class OrderPayConfirmation(View):
    def get(self,request,*args,**kwargs):
        return render(request,'customer/order_pay_confirmation.html')

class Menu(View):
    def get(self,request,*args,**kwargs):
        menu_items=MenuItem.objects.all()

        context={  
            'menu_items':menu_items
        }

        return render(request,'customer/menu.html',context)

class MenuSearch(View):
    def get(self,request,*args,**kwargs):
        query=self.request.GET.get("q")

        menu_items=MenuItem.objects.filter(
            Q(name__icontains=query)|
            Q(price__icontains=query)|
            Q(description__icontains=query)
        )

        context={
            'menu_items': menu_items
        }

        return render(request,'customer/menu.html',context)