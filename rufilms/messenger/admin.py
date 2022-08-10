from django.contrib import admin
from . import models
from .forms import PhraseForm, SubtitleForm, ScriptForm, ButtonForm


@admin.register(models.Phrases)
class PhraseAdmin(admin.ModelAdmin):
    form=PhraseForm  # custom form for admin phrase


@admin.register(models.Subtitle)
class SubtitleAdmin(admin.ModelAdmin):
    form = SubtitleForm


@admin.register(models.Script)
class ScriptAdmin(admin.ModelAdmin):
    form= ScriptForm


@admin.register(models.Button)
class ButtonAdmin(admin.ModelAdmin):
    form= ButtonForm


admin.site.register(models.Message)
admin.site.register(models.VideoFiles)  # just default admin form for videofile


# Register your models here.
