from store.models import Product

from django.contrib import admin

# Register your models here.
from django.contrib.contenttypes.admin import GenericTabularInline

# from store.admin import ProductAdmin
from tags.models import TaggedItem
from . import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "email", "first_name", "last_name"),
            },
        ),
    )
# class TagInline(GenericTabularInline):
#     model = TaggedItem
#
#
# class CustomProductAdmin(ProductAdmin):
#     inlines = [TagInline]
#
# admin.site.unregister(Product)
# admin.site.register(Product, CustomProductAdmin)
