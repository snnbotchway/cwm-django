from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin, ProductImageInline
from store.models import Product, ProductImage
from tags.models import TaggedItem
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # add first name and last name to user registration field in admin panel
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "first_name", "last_name"),
            },
        ),
    )


class TagInline(GenericTabularInline):
    model = TaggedItem
    extra = 0
    autocomplete_fields = ['tag']


# show products with their tags in admin panel
class LinkedProductAdmin(ProductAdmin):
    inlines = [TagInline, ProductImageInline]


admin.site.unregister(Product)
admin.site.register(Product, LinkedProductAdmin)
