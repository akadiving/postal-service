from django.db.models.query import QuerySet
from django.shortcuts import render
from rest_framework import permissions
from rest_framework.generics import ListAPIView, CreateAPIView, \
RetrieveUpdateAPIView, RetrieveDestroyAPIView
from .models import Item
from .serializers import ItemSerializer
from rest_framework.response import Response
# Create your views here.

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user

class ItemListView(ListAPIView,IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        else:
            return self.queryset.filter(owner=owner)


class AddItemView(CreateAPIView,IsOwnerOrReadOnly):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UpdateItemView(RetrieveUpdateAPIView,IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        else:
            return self.queryset.filter(owner=owner)

class DeleteItemView(RetrieveDestroyAPIView,IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        else:
            return self.queryset.filter(owner=owner)

