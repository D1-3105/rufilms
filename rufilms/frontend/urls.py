from django.urls import path
from .views import TV
urlpatterns = [
    path('', TV.as_view(), name='front'),
]
