from django.urls import path
from .views import MessageView, GreetingView

urlpatterns=[
    path('', MessageView.as_view(),name='message'),
    path('greeting/', GreetingView.as_view(), name='greeting')
]