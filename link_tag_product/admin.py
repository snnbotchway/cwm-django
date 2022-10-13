from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem


class TagInline(GenericTabularInline):
    model = TaggedItem
    extra = 0
    autocomplete_fields = ['tag']


class LinkedProductAdmin(ProductAdmin):
    inlines = [TagInline]


admin.site.unregister(Product)
admin.site.register(Product, LinkedProductAdmin)
