from django.urls import path
from .views import *


urlpatterns = [
    path('api/register/', RegisterUserView.as_view(), name='register'),
    path('api/logout/', BlacklistTokenUpdateView.as_view(), name="logout"),
]
