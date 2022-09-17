from rest_framework import serializers
from messenger.models import Phrases
lang_kit={
    'rus':"<субтитров к данному видео не существует!>",
    'eng':'<there are no subtitles for current video!>'
}

class ReadableMessageClass:

    def __init__(self, sender, msg, detected_scheme):
        self.cookie=sender['anonimous_token']
        self.user_email=sender.get('email')
        self.user_name=sender.get('name')
        self.msg=msg
        videos_qs = Phrases.objects.filter_related_videos(detected_scheme)
        subtitles={}
        for lang in videos_qs.values_list('lang', flat=True):
            try:
                subtitles.update({lang: videos_qs.filter(lang=lang).exclude(subtitles=None).first().subtitles.text})
            except:
                subtitles.update({lang: lang_kit.get(lang, 'No subs')})
        self.bot_answer=subtitles

class ReadableMessageSerializer(serializers.Serializer):
    sender= serializers.DictField()
    msg= serializers.CharField()
    detected_scheme= serializers.IntegerField()

    def save(self, **kwargs):
        return self.create(validated_data=self.validated_data)

    def create(self, validated_data):
        return ReadableMessageClass(**validated_data)

    class Meta:
        fields='sender','msg','detected_scheme'

