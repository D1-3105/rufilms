from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# ffmpeg
import os
import subprocess
import random
import re
# post_save processor
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed
from django.conf import settings


def video_management(instance, filename):  # sets filepath using info of file
    return '/'.join([
        instance.lang,
        instance.avatar,
        instance.screen_size,
        instance.quality,
        #
        f'{instance.phrase.topic}.mp4'
        ]
    )


class LanguageChoices:
    choices=[(dir_name, _(dir_name)) for dir_name in os.listdir(settings.MEDIA_ROOT)]


class VideoFiles(models.Model):
    subtitles = models.ForeignKey(to='Subtitle', on_delete=models.SET_NULL, null=True, blank=True)
    phrase=models.ForeignKey(to="Phrases",
                             on_delete=models.SET_NULL,
                             null=True, blank=True)  # phrases should not be deleted if VideoFile deleted
    video_file=models.FileField(upload_to=video_management)
    quality=models.CharField(
        choices=(
            ('480p','480p'),
            ('720p', '720p'),
            ('1080p','1080p')
        ), max_length=5
    )
    screen_size = models.CharField(max_length=10)
    avatar= models.CharField(max_length=10)
    lang= models.CharField(max_length=10, choices=LanguageChoices.choices)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['phrase','screen_size','avatar','quality'],
                                    name='unique video-file')
        ]

    def __str__(self):
        return f'{self.video_file.path}'


    def get_meta_fields(self, plural=False): # returns list of attributes that not related to all files
        return [f.name
                for f in self._meta.get_fields()].remove('phrases')

    def get_filename(self):
        #  https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
        return str(re.search(r'[^\\/]+(?=[\\/]?$)', self.video_file.name).group(0))

    def delete(self, using=None, keep_parents=False):
        path=settings.MEDIA_ROOT/self.video_file.name
        try:
            os.remove(path)
        except:
            pass
            # do smth
        return super().delete(using, keep_parents)


@receiver(post_save, sender=VideoFiles)
def make_ffmpeg(instance, created=True, **kwargs):
    if created:
        ffmpeg=settings.FFMPEG_PATH
        video=str(settings.MEDIA_ROOT/instance.video_file.name).replace('\\','/')
        salt=''.join([chr(random.randint(65,90)) for _ in range(5)])
        old_filename=instance.get_filename()  # greeting.mp4
        after_dot=re.search(r'(?<=.)\w+\Z', old_filename).group(0)

        new_filename=re.search(r'\w+(?<=.)',old_filename).group(0)+salt+'.'+after_dot  # greatingXYZEW.mp4
        new_filepath=str(video).replace(old_filename, new_filename)  # D:\\..\\greatingXYZEW.mp4


        process= subprocess.Popen(f'{ffmpeg} -i {video} '
                                  f'-codec copy -map 0 -movflags +faststart {new_filepath}',
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        try:
            stdout, stderr = process.communicate()
            process.wait()
        except Exception as e:
            print("ERROR DURING PROCESSING:", str(e))

        os.remove(video)
        os.rename(new_filepath, video)


class ListField(models.Field):  # field with phrases

    def __init__(self, sep='&',*args, **kwargs):
        self.separator=sep
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        if isinstance(value, list):
            for phrase in value:
                if self.separator in phrase:
                    raise ValidationError(
                        _(f'{phrase} contains database separator!')
                    )
            return self.separator.join(value)

        if isinstance(value, str):
            return value.strip(' \n')

    def to_python(self, value):  # converts ""&""&"" to ("","","")
        if isinstance(value, list):
            return '&'.join(value)
        if isinstance(value, set):
            return '&'.join(value)
        if value is None:
            return value
        if isinstance(value, str):
            return value
        return value

    def deconstruct(self):
        args= super().deconstruct()
        return args

    def get_internal_type(self):
        return 'TextField'

    def from_db_value(self, value, expression, connection):
        return value.split('&')

    def get_prep_value(self, value):
        if isinstance(value, list):
            value=self.separator.join(value)  # it crashes in m2m_changed signal for script model
        return super().get_prep_value(value)


class Subtitle(models.Model):
    text = models.TextField(default='')
    video_file = models.ManyToManyField(to='VideoFiles')

    def __str__(self):
        return str(self.text[0:30])


@receiver(m2m_changed, sender=Subtitle.video_file.through)
def link_video_files(**kwargs):
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    if action=='post_add':
        for video_instance in VideoFiles.objects.filter(pk__in=pk_set):
            video_instance.subtitles = instance
            video_instance.save()
    if action=='post_remove':
        for video_instance in instance.video_file.filter(pk__in=pk_set):
            video_instance.subtitles.delete()
            video_instance.save()


class Script(models.Model):
    script_related_phrases = models.ManyToManyField(to='Phrases')
    script_name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.script_name


@receiver(m2m_changed, sender=Script.script_related_phrases.through)
def link_script_to_phrases(**kwargs):
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    if action == 'post_add':
        if len(pk_set)>0:
            first_phrase=Phrases.objects.get(pk=list(pk_set)[0])
            first_phrase.entry_of_scripts.add(instance.pk)
    if action == 'post_remove':
        phrases = Phrases.objects.filter(pk__in=pk_set, entry_of_scripts=instance)
        for phrase in phrases:
            phrase.entry_of_scripts.remove(instance.pk)
        #phrase.save()
    if action == 'post_clear':
        if len(pk_set)>0:
            first_phrase= Phrases.objects.get(pk=list(pk_set)[0])
            first_phrase.entry_of_scripts.remove(instance.pk)
        #first_phrase.save()


class PhrasesQuerySet(models.QuerySet):

    def filter_related_videos(self,pk):
        related_videos_qs = VideoFiles.objects.filter(phrase__pk=pk)
        return related_videos_qs

    def filter_related_subtitles(self,pk):
        related_videos_qs=self.filter_related_videos(pk)
        related_subtitles_qs=Subtitle.objects.filter(video_file__in=related_videos_qs)
        return related_subtitles_qs

class PhrasesManager(models.Manager):

    def get_queryset(self):
        return PhrasesQuerySet(self.model, self._db)

    def filter_related_videos(self, pk):
        return self.get_queryset().filter_related_videos(pk)

    def filter_related_subtitles(self, pk):
        return self.get_queryset().filter_related_subtitles(pk)


class Phrases(models.Model):
    phrases=ListField(sep='&', blank=True)
    topic = models.CharField(max_length=20, unique=True)
    entry_of_scripts = models.ManyToManyField(to='Script', blank=True)
    buttons = models.ManyToManyField(to='Button', blank=True)

    objects=PhrasesManager()

    def serializable_value(self, field_name):
        if field_name=='phrases':
            return '&'.join(super().serializable_value(field_name))
        else:
            return super().serializable_value(field_name)

    def __str__(self):
        return f'{self.topic}:{str(self.phrases)}'


@receiver(m2m_changed, sender=Phrases.entry_of_scripts.through)
def edit_start_phrase_script(**kwargs):
    action=kwargs.get('action')
    instance=kwargs.get('instance')
    pk_set=kwargs.get('pk_set')
    script_qs = Script.objects.filter(pk__in=pk_set)
    for script_instance in script_qs:
        if action=='post_add':
            values=[instance.pk]+list(script_instance.script_related_phrases.all().values_list('pk', flat=True))
            script_instance.script_related_phrases.set(values)
        if action=='post_remove':
            script_instance.script_related_phrases.remove(instance)


@receiver(m2m_changed, sender=Phrases.buttons.through)
def edit_linked_buttons(**kwargs):
    action = kwargs.get('action')
    instance = kwargs.get('instance')
    pk_set = kwargs.get('pk_set')

    button_qs = Button.objects.filter(pk__in=pk_set)
    for button_instance in button_qs:
        if action=='post_add':
            button_instance.button_related_phrases.add(instance)
        if action=='post_remove':
            button_instance.button_related_phrases.remove(instance)


class MessageQuerySet(models.QuerySet):

    def filter_new_messages(self):
        return self.filter(reported=False)


class MessageManager(models.Manager):

    def get_queryset(self):
        return MessageQuerySet(self.model, self._db)

    def filter_new_messages(self):
        return self.get_queryset().filter_new_messages()


class Message(models.Model):

    msg = models.TextField()
    detected_scheme = models.ForeignKey('Phrases',
                                        related_query_name='messenger_Message_related_Scheme',
                                        on_delete=models.SET_NULL, null=True
                                        )
    sender = models.ForeignKey('Sender', on_delete=models.CASCADE, null=True)
    reported = models.BooleanField(default=False)

    objects=MessageManager()


class Button(models.Model):
    text= models.TextField(default='')
    lang = models.CharField(max_length=10,choices=LanguageChoices.choices)
    button_related_phrases = models.ManyToManyField(to=Phrases, blank=True)

    def __str__(self):
        return 'text: {} ; lang: {} ; phrases: {}'.format(self.text[:10],
                         self.lang,
                         list(self.button_related_phrases.all().values_list('topic', flat=True)))


@receiver(m2m_changed, sender=Button.button_related_phrases.through)
def link_button_to_phrases(**kwargs):
    instance = kwargs.pop('instance', None)
    pk_set = kwargs.pop('pk_set', None)
    action = kwargs.pop('action', None)
    if action == 'post_add':
        if len(pk_set) > 0:
            phrases = Phrases.objects.filter(pk__in=list(pk_set))
            for phrase in phrases:
                phrase.buttons.add(instance.pk)
    if action == 'post_remove':
        phrases = Phrases.objects.filter(pk__in=list(pk_set), buttons=instance)
        for phrase in phrases:
            phrase.buttons.remove(instance.pk)
    if action == 'post_clear':
        if len(pk_set) > 0:
            phrases = Phrases.objects.filter(pk__in=list(pk_set))
            for phrase in phrases:
                phrase.buttons.remove(instance.pk)


class Sender(models.Model):
    email= models.EmailField()
    anonimous_token = models.TextField(unique=True)
    name= models.CharField(max_length=256)