from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin,LoginRequiredMixin
from django.utils.timezone import datetime
from customer.models import OrderModel
from django.core.mail import send_mail


# Create your views here.
class Dashboard(LoginRequiredMixin,UserPassesTestMixin,View):
    def get(self,request,*args,**kwargs):
        # Current Date
        today=datetime.today()
        orders=OrderModel.objects.filter(created_on__year=today.year,created_on__month=today.month,created_on__day=today.day)

        # Loop through orders and Price Value
        unshipped_orders=[]

        total_revenue=0
        for order in orders:
            total_revenue+=order.price

            if not order.is_shipped:
                unshipped_orders.append(order)

        #Pass total orders and Price into Template
        context={
            # 'orders':orders,
            'orders':unshipped_orders,
            'total_revenue':total_revenue,
            'total_orders':len(orders)

        }

        return render(request,'restaurant/dashboard.html',context)

    def test_func(self): #UserPassTestMixin Function being overriden
        return self.request.user.groups.filter(name='Staff').exists()
        
class OrderDetails(LoginRequiredMixin,UserPassesTestMixin,View):
    def get(self,request,pk,*args,**kwargs):
        order=OrderModel.objects.get(pk=pk)

        context={
            'order':order
        }

        return render(request,'restaurant/order-details.html',context) 

    def post(self,request,pk,*args,**kwargs):
        order=OrderModel.objects.get(pk=pk)
        order.is_shipped=True
        order.save()

        context={
            'order':order
        }

        if order.is_shipped==True:
            body=('Thank you for your Order ! Your Food has been prepared and is on the way !\n'
                f'Your Total:{order.price}\n'
                'Thank you again for your order!')

            #Confirmation Email
            send_mail(
                'Thank You for Your Order!!',
                body,
                'khaan-paan@khaan-paan.com',
                [order.email],
                fail_silently=False
            )

        return render(request,'restaurant/order-details.html',context)

    def test_func(self): #UserPassTestMixin Function being overriden
        return self.request.user.groups.filter(name='Staff').exists()