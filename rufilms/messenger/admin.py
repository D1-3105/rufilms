from django.contrib import admin
from . import models
from .forms import PhraseForm


@admin.register(models.Phrases)
class PhraseAdmin(admin.ModelAdmin):
    form=PhraseForm  # custom form for admin phrase


admin.site.register(models.VideoFiles)  # just default admin form for videofile



# Register your models here.
