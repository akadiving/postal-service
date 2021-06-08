from django.db.models.query import QuerySet
from django.shortcuts import render
from datetime import datetime
from rest_framework import permissions
from rest_framework.generics import ListAPIView, CreateAPIView, \
RetrieveUpdateAPIView, RetrieveDestroyAPIView
from .models import Item
from .serializers import ItemSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.generic import View
from .utils import render_to_pdf
from django.views.decorators.csrf import csrf_exempt
import json
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
        elif request.user.is_superuser:
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
        elif owner.is_anonymous:
            return None
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
        elif owner.is_anonymous:
            return None
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
        elif owner.is_anonymous:
            return None
        else:
            return self.queryset.filter(owner=owner)

@csrf_exempt
def GeneratePdf(request, pk):
    if not request.user.is_authenticated:
        return HttpResponse('You need to authenticate')
    elif request.user.is_anonymous:
        return HttpResponse('You are not allowed to visit this page')
    elif not request.method == "POST":
        return HttpResponse("Only POST method allowed")

    obj = Item.objects.get(id=pk)
    data = {
        'today': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        'customer': obj,
    }
    pdf = render_to_pdf('pdf/barcode_image.html', data)
    return HttpResponse(pdf, content_type='application/pdf')
    


