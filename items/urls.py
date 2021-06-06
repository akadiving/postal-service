from django.urls import path
from .views import ItemListView, AddItemView, UpdateItemView, DeleteItemView

urlpatterns = [
    path('', ItemListView.as_view(), name='item list'),
    path('add/', AddItemView.as_view(), name='add item'),
    path('update/<int:pk>', UpdateItemView.as_view(), name='update item'),
    path('delete/<int:pk>', DeleteItemView.as_view(), name='delete item'),
]
