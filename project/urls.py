from django.contrib import admin
from django.urls import path,include
from orders.DTL import IndexView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('api/', include('orders.urls')),

]
