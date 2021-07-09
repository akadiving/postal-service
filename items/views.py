from datetime import datetime
import requests
from django.db.models import Q
from rest_framework import permissions, filters, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, \
    RetrieveUpdateAPIView, RetrieveDestroyAPIView
from .utils import generate_zpl
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from .models import Item, Manifest
from .serializers import ItemSerializer, ManifestSerializer
from rest_framework.response import Response
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.db.models import Count
import xlwt
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

    def has_permission(self, request, view):
        if request.user.groups.filter(name='Company').exists() or request.user.is_superuser:
            return True
        return False


class IsOwnerFilterBackend(filters.BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(owner=request.user)


class IteamSearchView(ListAPIView, IsOwnerOrReadOnly):
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
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
        serializer.save(owner=self.request.user,
                        company=self.request.user.company_name)


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


'''
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
        'weight': obj.weight/100
    }

    template_path = 'pdf/barcode_image.html'
    response = HttpResponse(content_type='application/pdf')
    html = render_to_string(template_path, data)

    pisaStatus = pisa.CreatePDF(html, dest=response)

    return response

'''


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, IsOwnerOrReadOnly))
def GeneratePdf(request, pk):
    '''
        This function takes ID of item as an argument and generates invoice
        which is a conversion of zpl command to a PDF file.

        It also utilizes third party API to make this conversion possible + a request library
    '''
    # Check if user is authenticated.
    if request.user.is_anonymous:
        message = {'message': 'You are not allowed to visit this page'}
        return JsonResponse(message, safe=False)

    # get an object with id
    obj = Item.objects.get(id=pk)

    # take an object values do generate variables in pdf
    data = [str(obj.barcode), str(obj.get_sender_full_name()),
            str(obj.sender_city), str(obj.weight),
            str(obj.get_receiver_full_name()), str(obj.receiver_number),
            str(obj.receiver_city), datetime.now().strftime(
                "%d-%m-%Y %H:%M:%S"),
            str(obj.owner.company_name)
            ]

    # insert variables in zpl command (check utils.py to find funciton bellow)
    zpl = generate_zpl(*data)
    url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
    files = {'file': zpl}
    # omit this line to get PNG images back
    headers = {'Accept': 'application/pdf'}
    response = requests.post(url, headers=headers, files=files, stream=True)

    if response.status_code == 200:
        response.raw.decode_content = True
        # convert response to a readable stream
        response = HttpResponse(
            content=response, content_type=response.headers['Content-Type'])
        return response
    else:
        print('Error: ' + response.text)
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

    columns = ['გზ.ნომერი', 'პირადი ნომერი', 'სახელი', 'გვარი', 'ტელეფონი',
               'მისამართი', 'ქვეყანის კოდი', 'წონა', 'გზ. ტიპი', 'დაბ.ტიპი', 'რეგ.თარიღი',
               'საწყობში შემოტანის თარიღი', 'დოკუმენტის ნომერი', 'ტრანსპორტირების ხარჯები 1',
               'ტრანსპორტირების ხარჯები 1-ის ვალუტა', 'ტრანსპორტირების ხარჯები  2',
               'ტრანსპორტირების ხარჯები 2-ის ვალუტა', 'ტრანსპორტირების სხვა ხარჯები',
               'ტრანსპორტირების სხვა ხარჯების ვალუტა', 'მაღაზიის სახელი', 'შენიშვნა' 'რეისის ნომერი',
               'დაბრუნებული']

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
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticated]
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
