from django.contrib import admin
from .models import *

class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1  

class ExpiryInline(admin.TabularInline):
    model = Expiry
    extra = 1

class UserItemInline(admin.TabularInline):
    model = UserItem
    extra = 1

admin.site.register(Category)
admin.site.register(userhistory)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    inlines = [ItemImageInline, UserItemInline, ExpiryInline]

admin.site.register(ItemImage)
admin.site.register(UserItem)
admin.site.register(CustomUser)

@admin.register(Expiry)
class ExpiryAdmin(admin.ModelAdmin):
    list_display = ('item', 'date', 'quantity')