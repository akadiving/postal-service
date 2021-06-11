from rest_framework import serializers
from .models import Item, Manifest


# serializer for Item Model
class ItemSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    manifest_number_id = serializers.PrimaryKeyRelatedField(
        queryset=Manifest.objects.all(),
        source='manifest_number', 
        required=False,
        allow_null=True, default=None)

    class Meta:
        model = Item
        exclude = ['created_at']
        read_only_fields = ['barcode', 'owner']
    
# serializer for Manifest Model
class ManifestSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    total_items = serializers.IntegerField(allow_null=True)
    items = ItemSerializer(many=True, source='item') # Returns the list of items in manifest

    class Meta:
        model = Manifest
        fields =['id','owner','created_at','sender_city','receiver_city',
                'manifest_code','cmr','car_number','total_items','items']
        read_only_fields = ['manifest_code', 'owner', 'created_at']

    
