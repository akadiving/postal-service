from django.contrib import admin
from .models import Item, Manifest, Shelf
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportActionModelAdmin
# Register your models here.


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'created_at', 'owner', 'sender_name', 'sender_surname', 'company',
        'sender_country', 'sender_city', 'receiver_name', 'receiver_surname',
        'receiver_id', 'receiver_country', 'receiver_city', 'receiver_address',
        'receiver_number', 'description', 'weight', 'price', 'barcode',
        'manifest_number', 'shelf_number', 'delivered'
    ]


@admin.register(Manifest)
class ManifestAdmin(ImportExportActionModelAdmin, ImportExportModelAdmin):
    list_display = [
        'created_at', 'owner', 'car_number', 'driver_name', 'driver_surname', 'cmr', 'manifest_code',
        'receiver_city', 'sender_city'
    ]


@admin.register(Shelf)
class ManifestAdmin(ImportExportActionModelAdmin, ImportExportModelAdmin):
    list_display = [
        'created_at', 'owner', 'name',
    ]
