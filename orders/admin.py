from django.contrib import admin
from .models import Order, Product, Company
import csv
from django.http import HttpResponse
from django.utils import timezone

@admin.action(description='Delete selected products') # marked as inactive instead of deleting
def mark_products_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False, last_updated_at=timezone.now())


class ProductAdmin(admin.ModelAdmin):
    actions = [mark_products_inactive]

    def get_actions(self, request):
        actions = super().get_actions(request)
        print(actions)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions



admin.site.register(Product, ProductAdmin)
@admin.action(description='Export selected orders as CSV')
def export_orders_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Product', 'Company', 'User', 'Status'])  # Add your fields here
    for order in queryset:
        writer.writerow([order.id, order.product, order.company, order.user, order.status])  # Adjust fields as necessary
    return response

class OrderAdmin(admin.ModelAdmin):
    actions = [export_orders_as_csv]

admin.site.register(Order, OrderAdmin)

admin.site.register(Company)