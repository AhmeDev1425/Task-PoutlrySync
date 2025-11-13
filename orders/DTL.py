
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','price','stock']

class IndexView(TemplateView):
    template_name = 'orders/index.html'

    def get(self, request,*a,**k):
        if not request.user.is_authenticated:
            return redirect('admin/login/')
        form = ProductForm()
        products = Product.active_objects.filter(company=request.user.company)
        total_stock = sum(p.stock for p in products)
        avg = total_stock / products.count() if products.exists() else 0
        return self.render_to_response({'form':form,'total_stock':total_stock,'price_avg': avg ,'products':products})


    def post(self, request,*a,**k):
        if not request.user.is_authenticated:
            return redirect('admin/login/')
        
        form = ProductForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.company = request.user.company
            p.created_by = request.user
            p.save()
            return redirect('index')
        products = Product.active_objects.filter(company=request.user.company)
        total_stock = sum(p.stock for p in products)
        avg = total_stock / products.count() if products.exists() else 0
        return self.render_to_response({'form':form,'total_stock':total_stock,'price_avg': avg ,'products':products})
