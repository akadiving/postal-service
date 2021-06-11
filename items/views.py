from datetime import datetime
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, \
RetrieveUpdateAPIView, RetrieveDestroyAPIView
from rest_framework.decorators import api_view, permission_classes
from .models import Item, Manifest
from .serializers import ItemSerializer, ManifestSerializer
from rest_framework.response import Response
from django.http import HttpResponse
import json
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import JsonResponse
from django.db.models import Count
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
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
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

@api_view(['GET','POST'])
@permission_classes((IsAuthenticated,IsOwnerOrReadOnly))
def GeneratePdf(request, pk):
    # Check if user is authenticated.
    if request.user.is_anonymous:
        message = {'message': 'You are not allowed to visit this page'}
        return JsonResponse(message, safe=False)

    obj = Item.objects.get(id=pk)
    data = {
        'today': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        'customer': obj,
    }
    
    template_path = 'pdf/barcode_image.html'
    response = HttpResponse(content_type='application/pdf')
    html = render_to_string(template_path, data)

    pisaStatus = pisa.CreatePDF(html, dest=response)

    return response
  
class ManifestListView(ListAPIView,IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Manifest.objects.annotate(total_items=Count('item'))
    serializer_class = ManifestSerializer

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        elif owner.is_anonymous:
            return None
        else:
            return self.queryset.filter(owner=owner)

class AddManifestView(CreateAPIView,IsOwnerOrReadOnly):
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UpdateManifestView(RetrieveUpdateAPIView,IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        elif owner.is_anonymous:
            return None
        else:
            return self.queryset.filter(owner=owner)

class DeleteManifestView(RetrieveDestroyAPIView,IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        elif owner.is_anonymous:
            return None
        else:
            return self.queryset.filter(owner=owner)
