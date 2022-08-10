from rest_framework import serializers
from messenger.models import Phrases


class ReadableMessageClass:

    def __init__(self, anonimous_token, msg, detected_scheme):
        self.cookie=anonimous_token
        self.msg=msg
        videos_qs = Phrases.objects.filter_related_videos(detected_scheme)
        subtitles = {
            lang: videos_qs.filter(lang=lang).first().subtitles.text
            for lang in videos_qs.values_list('lang', flat=True)
        }
        self.bot_answer=subtitles


class ReadableMessageSerializer(serializers.Serializer):
    anonimous_token= serializers.CharField()
    msg= serializers.CharField()
    detected_scheme= serializers.IntegerField()

    def save(self, **kwargs):
        return self.create(validated_data=self.validated_data)

    def create(self, validated_data):
        return ReadableMessageClass(**validated_data)

    class Meta:
        fields='anonimous_token','msg','detected_scheme'

