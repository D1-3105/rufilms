from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
# ffmpeg
import os
import subprocess
from sys import platform
import random
import re
# post_save processor
from django.dispatch import receiver
from django.db.models.signals import post_save
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


class VideoFiles(models.Model):
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
    lang= models.CharField(max_length=10)

    def get_filename(self):
        return str(re.search(r'[^\\/]+(?=[\\/]?$)', self.video_file.name).group(0))

    def delete(self, using=None, keep_parents=False):
        path=settings.MEDIA_ROOT/self.video_file.name
        try:
            os.remove(path)
        except:
            pass
        # do smth
        return super().delete(using, keep_parents)

    class Meta:
        constraints=[
            models.UniqueConstraint(fields=['phrase','screen_size','avatar','quality'],
                                    name='unique video-file')
        ]


@receiver(post_save, sender=VideoFiles)
def make_ffmpeg(instance, created=True, **kwargs):
    ffmpeg=settings.FFMPEG_PATH
    video=settings.MEDIA_ROOT/instance.video_file.name
    salt=''.join([chr(random.randint(65,90)) for _ in range(5)])
    old_filename=instance.get_filename()  # greeting.mp4
    after_dot=re.search(r'(?<=.)\w+\Z', old_filename).group(0)

    new_filename=re.search(r'\w+(?<=.)',old_filename).group(0)+salt+'.'+after_dot  # greatingXYZEW.mp4
    new_filepath=str(video).replace(old_filename, new_filename)  # D:\\..\\greatingXYZEW.mp4
    print(video, new_filepath)


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
                print(phrase)
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


class Phrases(models.Model):
    phrases=ListField(sep='&', blank=True)
    topic = models.CharField(max_length=20, unique=True)

    def serializable_value(self, field_name):
        if field_name=='phrases':
            return '&'.join(super().serializable_value(field_name))
        else:
            return super().serializable_value(field_name)

    def __str__(self):
        return f'{self.topic}:{str(self.phrases)}'