from rest_framework import serializers, exceptions
from . import models
from .utils import get_video_len
from .models import Message, Sender


class SenderSerializer(serializers.ModelSerializer):


    class Meta:
        fields='name', 'anonimous_token', 'email'
        model = Sender



class VideoFileSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data={
            'phrase':PhraseSerializer(instance.phrase).data,
            'subtitles': instance.subtitles.pk,
            'quality':instance.quality,
            'screen_size':instance.screen_size,
            'avatar':instance.avatar,
            'lang':instance.lang
        }
        return data

    class Meta:
        fields='phrase',\
               'subtitles',\
               'video_file',\
               'quality',\
               'screen_size',\
               'avatar',\
               'lang'


class SubtitleSerializer(serializers.ModelSerializer):

    class Meta:
        fields='text','video_file'


class PhraseSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            'topic':instance.topic,
            'entry_of_script': ScriptSerializer(instance.entry_of_script).data,
            'phrases':instance.phrases
        }

    class Meta:
        fields='topic','entry_of_script','phrases'
        model=models.Phrases


class MessageSerializer(serializers.ModelSerializer):  # allows to
    msg=serializers.CharField()
    detected_scheme = serializers.PrimaryKeyRelatedField(required=False, queryset=models.Phrases.objects.all())
    sender= serializers.CharField(required=False)

    def validate(self, data):
        anon_tok=self.context['request'].COOKIES.get('anonimous_token', None)
        if not anon_tok:
            raise exceptions.ValidationError(
                {"anonimous_token":"This cookie required"}
            )
        sender_qs=Sender.objects.filter(anonimous_token=anon_tok)
        if not sender_qs.exists():
            raise exceptions.ValidationError(
                {'anonimous_token':'Related object not found'}
            )
        data['sender'] = sender_qs.get()
        return data

    def to_representation(self, instance):
        data={
            'msg': instance.msg,
            'detected_scheme': instance.detected_scheme.pk,
            'sender': SenderSerializer(instance.sender).data
        }
        return data

    class Meta:
        fields=('msg','detected_scheme','sender',)
        model=Message


class ScriptSerializer(serializers.ModelSerializer):
    pk = serializers.PrimaryKeyRelatedField(queryset=models.Script.objects.all())

    class Meta:
        model = models.Script
        fields='pk',


class ScriptPositionSerializer(serializers.Serializer):
    position = serializers.IntegerField()
    pk= serializers.IntegerField()

    def get_position(self):
        return self.validated_data.get('position')

    class Meta:
        fields = 'position', 'pk'


class VideoSerializer(serializers.Serializer):
    # durability= serializers.FloatField(required=True)
    scheme_pk=serializers.IntegerField()

    def validate_buttons(self, scheme_pk):
        return ButtonSerializer(
            models.Phrases.objects.get(pk=scheme_pk).buttons,
            many=True
        ).data

    def validate(self, data):
        #  convert data to json
        videos= models.Phrases.objects.filter_related_videos(data['scheme_pk'])
        video_file_instance=videos.first()
        durability = get_video_len(video_file_instance.video_file.path)
        #
        avatars=set()
        qualities=set()
        screens=set()
        langs=set()
        for video in videos:
            avatars.add(video.avatar)
            qualities.add(video.quality)
            screens.add(video.screen_size)
            langs.add(video.lang)
        subtitles = {
            lang: videos.filter(lang=lang).first().subtitles.text
            for lang in videos.values_list('lang', flat=True)
        }
        script=models.Phrases.objects.get(pk=data['scheme_pk']).entry_of_scripts.all()
        #
        validated_data = {
            'durabity': durability,
            'video_name': video_file_instance.get_filename(),
            'avatars': list(set(avatars)),
            'qualities': list(set(qualities)),
            'screens': list(set(screens)),
            'lang': list(langs),
            'actions':{
                'subtitles': subtitles,
                'script': script.values_list('pk', flat=True),
                'buttons': self.validate_buttons(scheme_pk=data['scheme_pk'])
            }
        }
        return validated_data

    class Meta:

        fields=('scheme_pk',)

class ButtonSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        return {
            instance.lang: instance.text
        }

    class Meta:
        fields = 'text', 'lang'