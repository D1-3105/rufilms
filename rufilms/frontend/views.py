from django.shortcuts import render
from django.views.generic import TemplateView


class TV(TemplateView):
    template_name = 'frontend/index.html'
# Create your views here.
