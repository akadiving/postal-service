from django.db.models.query import QuerySet
from rest_framework import serializers
from django.db.models import Sum
from .models import Item, Manifest


# serializer for Item Model
class ItemSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source='owner.username', read_only=True)
    manifest_number = serializers.PrimaryKeyRelatedField(
        queryset=Manifest.objects.all(),
        # source='manifest_number.manifest_code',
        required=False,
        allow_null=True, default=None)
    manifest_code = serializers.CharField(
        source='manifest_number.manifest_code',
        required=False,
        allow_null=True, default=None
    )
    in_manifest = serializers.BooleanField(allow_null=True, default=False)

    class Meta:
        model = Item
        exclude = ['created_at', ]
        read_only_fields = ['barcode', 'owner']

    def create(self, validated_data):
        return Item.objects.create(**validated_data)


# serializer for Manifest Model


class ManifestSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    created_at = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", read_only=True)
    total_items = serializers.SerializerMethodField()
    # Returns the list of items in manifest
    items = ItemSerializer(many=True, source='item', read_only=True)
    total_weight = serializers.SerializerMethodField()

    class Meta:
        model = Manifest
        fields = ['id', 'owner', 'created_at', 'sender_city', 'receiver_city',
                  'manifest_code', 'cmr', 'car_number', 'total_items', 'total_weight', 'items']
        read_only_fields = ['manifest_code', 'owner', 'created_at', 'items']

    def get_total_weight(self, obj):
        return obj.item.aggregate(Sum('weight'))['weight__sum']

    def get_total_items(self, obj):
        return obj.item.count()
