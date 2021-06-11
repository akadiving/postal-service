from django.urls import path
from .views import *

urlpatterns = [
    # Item views
    path('', ItemListView.as_view(), name='item list'),
    path('add/', AddItemView.as_view(), name='add item'),
    path('update/<int:pk>', UpdateItemView.as_view(), name='update item'),
    path('delete/<int:pk>', DeleteItemView.as_view(), name='delete item'),
    path('generate-pdf/<int:pk>', GeneratePdf, name='generate pdf'),

    # Manifest views
    path('manifest/', ManifestListView.as_view(), name='manifest list'),
    path('manifest/add/', AddManifestView.as_view(), name='add manifest'),
    path('manifest/update/<int:pk>', UpdateManifestView.as_view(), name='update manifest'),
    path('manifest/delete/<int:pk>', DeleteManifestView.as_view(), name='delete manifest'),
]
