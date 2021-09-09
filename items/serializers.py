from django.db.models.query import QuerySet
from rest_framework import serializers
from django.db.models import Sum
from .models import Item, Manifest


# serializer for Item Model
class ItemSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source='owner.username', read_only=True)
    company = serializers.CharField(
        source='owner.company_name', read_only=True)
    manifest_number = serializers.PrimaryKeyRelatedField(
        queryset=Manifest.objects.all(),
        required=False,
        allow_null=True, default=None)
    manifest_code = serializers.CharField(
        source='manifest_number.manifest_code',
        required=False,
        allow_null=True, default=None,
        read_only=True
    )
    signature = serializers.SerializerMethodField()

    class Meta:
        model = Item
        exclude = [ 'shelf_number', ]
        read_only_fields = ['barcode', 'owner', 'company', 'manifest_code', 'signature', 'created_at']

    def create(self, validated_data):
        return Item.objects.create(**validated_data)

    def get_signature(self, obj):
        if obj.signature:
            return 'https://apimyposta.online' + obj.signature.url
        return ''

# serializer for Manifest Model


class ManifestSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    company = serializers.CharField(
        source='owner.company_name', read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True)
    total_items = serializers.SerializerMethodField()
    # Returns the list of items in manifest
    items = ItemSerializer(many=True, source='item',
                           read_only=True, partial=True)
    total_weight = serializers.SerializerMethodField()

    class Meta:
        model = Manifest
        fields = ['id', 'owner', 'company', 'created_at', 'sender_city', 'receiver_city',
                  'manifest_code', 'cmr', 'car_number', 'driver_name', 'driver_surname', 'total_items', 'total_weight', 'items']
        read_only_fields = ['manifest_code', 'owner',
                            'created_at', 'items', 'company']

    def get_total_weight(self, obj):
        return obj.item.aggregate(Sum('weight'))['weight__sum']

    def get_total_items(self, obj):
        return obj.item.count()
