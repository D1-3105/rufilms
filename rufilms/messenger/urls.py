from django.urls import path
from .views import MessageAPIView, GreetingAPIView, ScriptAPIView

urlpatterns=[
    path('', MessageAPIView.as_view(),name='message'),
    path('greeting/', GreetingAPIView.as_view(), name='greeting'),
    path('script/', ScriptAPIView.as_view(), name='script')
]