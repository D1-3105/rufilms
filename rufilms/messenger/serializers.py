from rest_framework import serializers
from . import models
from .utils import get_video_len
import re

class PhraseSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            instance.pk:instance.phrases
        }

    class Meta:
        fields='__all__',
        model=models.Phrases


class MessageSerializer(serializers.Serializer):  # allows to
    msg=serializers.CharField()

    class Meta:
        fields=('msg',)


class VideoSerializer(serializers.Serializer):
    # durability= serializers.FloatField(required=True)
    scheme_pk=serializers.IntegerField()

    def get_queryset(self, pk):
        return models.VideoFiles.objects.filter(phrase__pk=pk)

    def validate(self, data):
        #  convert data to json
        videos= self.get_queryset(data['scheme_pk'])
        video_file_instance=videos.first()
        durability = get_video_len(video_file_instance.video_file.path)
        #
        avatars=[]
        qualities=[]
        screens=[]
        langs=[]
        for video in videos:
            avatars.append(video.avatar)
            qualities.append(video.quality)
            screens.append(video.screen_size)
            langs.append(video.lang)
        #
        validated_data = {
            'durabity': durability,
            'video_name': video_file_instance.get_filename(),
            #  https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
            #  make sure lists are unique
            'avatars': list(set(avatars)),
            'qualities': list(set(qualities)),
            'screens': list(set(screens)),
            'lang': list(set(langs))
        }
        return validated_data

    class Meta:

        fields=('scheme_pk',)