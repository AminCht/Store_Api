from django.contrib import admin, messages
from django.db.models import Count, QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode

from . import models


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    def products_count(self, collection):
        url = reverse('admin:store_product_changelist') + '?' + urlencode({'collection__id': str(collection.id)})
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'
    def lookups(self, request, model_admin):
        return [
            ('<10', 'low')
        ]

    def queryset(self, request, queryset:QuerySet):
        if self.value == '<10':
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'collection', 'inventory_status', 'collection']
    list_editable = ['unit_price']
    list_per_page = 10
    list_filter = ['collection', InventoryFilter]
    actions = ['clear_inventory']
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'low'
        return 'OK'

    @admin.action(description='clear inventory')
    def clear_inventory(self, request,queryset:QuerySet):
        updated_count = queryset.update(inventory=0)
        self.message_user(request, f'{updated_count} products edited successfully',
        messages.ERROR)

    prepopulated_fields = {
        'slug': ['title']
    }


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    ordering = ['user__first_name', 'user__last_name']
    list_select_related = ['user']
    list_per_page = 10
    search_fields = ['user__first_name', 'user__last_name']

    def orders_count(self, customer):
        return customer.orders_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'customer']
