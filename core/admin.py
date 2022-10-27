from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin):
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


class LinkedProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, LinkedProductAdmin)
