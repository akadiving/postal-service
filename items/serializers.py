from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)

    class Meta:
        model = Item
        exclude = ['created_at']
        read_only_fields = ['barcode', 'owner']
