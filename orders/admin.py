from django.contrib import admin
from django.utils import timezone
from .models import Order, Product, Company, User
from .utils import export_order_util

@admin.action(description='Delete selected products')
def mark_products_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False, last_updated_at=timezone.now())

class ProductAdmin(admin.ModelAdmin):
    actions = [mark_products_inactive]

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

@admin.action(description='Export selected orders as CSV')
def export_orders_as_csv(modeladmin, request, queryset):
    return export_order_util(queryset)

class OrderAdmin(admin.ModelAdmin):
    actions = [export_orders_as_csv]

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Company)
admin.site.register(User)
