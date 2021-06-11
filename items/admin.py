from django.contrib import admin
from .models import Item, Manifest
# Register your models here.

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'created_at','owner','sender_name','sender_surname','company',
        'sender_country', 'sender_city','receiver_name','receiver_surname',
        'receiver_id','receiver_country','receiver_city','receiver_address',
        'receiver_number','description','weight','price','barcode','in_manifest',
        'manifest_number'
        ]

@admin.register(Manifest)
class ManifestAdmin(admin.ModelAdmin):
    list_display = [
        'created_at','owner','car_number','cmr','manifest_code',
        'receiver_city','sender_city'
        ]