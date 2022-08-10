from django.urls import path
from .views import MessageAPIView, GreetingAPIView, ScriptAPIView, AuthAPIView, IntroductionAPIView

urlpatterns=[
    path('', MessageAPIView.as_view(),name='message'),
    path('greeting/', GreetingAPIView.as_view(), name='greeting'),
    path('script/', ScriptAPIView.as_view(), name='script'),
    path('auth/', AuthAPIView.as_view(), name='auth_cookie'),
    path('intro/', IntroductionAPIView.as_view(), name='introduction_messenger')
]