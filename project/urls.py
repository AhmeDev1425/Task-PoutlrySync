from django.contrib import admin
from django.urls import path, include
from orders.DTL import IndexView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Ordering System API",
        default_version='v1',
        description="API documentation for Ordering System",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)


from django.contrib.auth import logout
from django.shortcuts import redirect
def swagger_logout(request):
    logout(request)
    return redirect('/swagger/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('api/', include('orders.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),

    # Redoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),

]
