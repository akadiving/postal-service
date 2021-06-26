from datetime import datetime
from functools import partial
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import permissions, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, \
    RetrieveUpdateAPIView, RetrieveDestroyAPIView

from django.forms.models import model_to_dict
from rest_framework.views import APIView
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
import xlwt
from rest_framework.exceptions import APIException
# Create your views here.


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        # if request.method in permissions.SAFE_METHODS:
        # return True
        if request.user.is_superuser:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)


class IteamSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^barcode', '^owner__username',
                     '^sender_name', '^receiver_id']

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        elif owner.is_anonymous:
            return None
        else:
            return self.queryset.filter(owner=owner)


class ItemListView(ListAPIView, IsOwnerOrReadOnly):
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


class AddItemView(CreateAPIView, IsOwnerOrReadOnly):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UpdateItemView(RetrieveUpdateAPIView, IsOwnerOrReadOnly):
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


class DeleteItemView(RetrieveDestroyAPIView, IsOwnerOrReadOnly):
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


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
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


@api_view(['GET', 'POST', 'PATCH'])
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
def change_manifest(request):
    # Check if user is authenticated.
    if request.user.is_anonymous:
        message = {'message': 'You are not allowed to visit this page'}
        return JsonResponse(message, safe=False)
    elif request.method != 'PATCH':
        message = {'message': 'You can use only PATCH method'}
        return JsonResponse(message, safe=False)
    obj = Item.objects.filter(id__in=request.data['id'])
    obj.update(
        manifest_number=request.data['manifest'])
    print(request.method)
    serializer = ItemSerializer(data=obj, many=True, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
def delete_multiple_items(request):
    # Check if user is authenticated.
    if request.user.is_anonymous:
        message = {'message': 'You are not allowed to visit this page'}
        return JsonResponse(message, safe=False)
    elif request.method != 'DELETE':
        message = {'message': 'You can use only DELETE method'}
        return JsonResponse(message, safe=False)
    obj = Item.objects.filter(id__in=request.data['id'])
    obj.delete()
    print(request.data)
    serializer = ItemSerializer(data=obj, many=True, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
def export_excel(request, pk):
    # Check if user is authenticated.
    if request.user.is_anonymous:
        message = {'message': 'You are not allowed to visit this page'}
        return JsonResponse(message, safe=False)

    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Manifest' + \
        datetime.now().strftime("%d-%m-%Y %H:%M:%S") + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('მანიფესტი')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['id', 'ავტორი', 'დრო', 'გამგზავნი ქალაქი', 'მიმღები ქალაქი',
               'მანიფესტის კოდი', 'CMR კოდი', 'მანქანის ნომერი', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Manifest.objects.filter(id=pk).values_list('id', 'owner__username', 'created_at', 'sender_city', 'receiver_city',
                                                      'manifest_code', 'cmr', 'car_number',)

    item_rows = Item.objects.filter(manifest_number=pk).values_list()

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


class ManifestListView(ListAPIView, IsOwnerOrReadOnly):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
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


class ManifestSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['^manifest_code', '^owner__username',
                     '^car_number', '^sender_city', '^receiver_city']

    def get_queryset(self):
        owner = self.request.user
        if owner.is_superuser:
            return self.queryset.all()
        elif owner.is_anonymous:
            return None
        else:
            return self.queryset.filter(owner=owner)


class ManifestDetailView(IsOwnerOrReadOnly, RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer


class AddManifestView(CreateAPIView, IsOwnerOrReadOnly):
    queryset = Manifest.objects.all()
    serializer_class = ManifestSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class UpdateManifestView(RetrieveUpdateAPIView, IsOwnerOrReadOnly):
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


class DeleteManifestView(RetrieveDestroyAPIView, IsOwnerOrReadOnly):
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
