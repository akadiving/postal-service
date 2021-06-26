from django.urls import path
from .views import *

urlpatterns = [
    # Item views
    path('items/', ItemListView.as_view(), name='item-list'),
    path('items/search/', IteamSearchView.as_view(), name='item-search'),
    path('items/add/', AddItemView.as_view(), name='add-item'),
    path('items/update/<int:pk>', UpdateItemView.as_view(), name='update-item'),
    path('items/delete/<int:pk>', DeleteItemView.as_view(), name='delete-item'),
    path('items/generate-pdf/<int:pk>', GeneratePdf, name='generate-pdf'),
    path('items/update-manifest/', change_manifest, name='update-manifest'),
    path('items/bulk-delete/', delete_multiple_items, name='bulk-delete'),

    # Manifest views
    path('manifest/', ManifestListView.as_view(), name='manifest-list'),
    path('manifest/<int:pk>', ManifestDetailView.as_view(), name='manifest-detail'),
    path('manifest/search/', ManifestSearchView.as_view(), name='manifest-search'),
    path('manifest/add/', AddManifestView.as_view(), name='add-manifest'),
    path('manifest/update/<int:pk>',
         UpdateManifestView.as_view(), name='update-manifest'),
    path('manifest/delete/<int:pk>',
         DeleteManifestView.as_view(), name='delete-manifest'),
    path('manifest/export-excel/<int:pk>', export_excel, name='export-excel'),
]
