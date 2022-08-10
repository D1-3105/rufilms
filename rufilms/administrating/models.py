from django.db import models
from django.utils.translation import gettext_lazy as _


class LangChoices(models.TextChoices):
    ENG = ('eng', _('English'))
    RUS = ('rus', _('Russian'))


class MailReceiver(models.Model):
    receiver_name = models.CharField(max_length=20, default='Administrator')
    receiver_email = models.EmailField(max_length=254)
    message_language = models.CharField(max_length=4,choices=LangChoices.choices)

    class Meta:
        verbose_name = 'e-Mail Receiver'
        verbose_name_plural = 'e-Mail Receivers'

    def __str__(self):
        return f'{self.receiver_email} - {self.receiver_name}'

# Create your models here.
