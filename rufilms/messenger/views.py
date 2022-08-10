# rest
from rest_framework.views import APIView, Response
from rest_framework.permissions import AllowAny
# local
from .serializers import MessageSerializer, VideoSerializer, ScriptPositionSerializer, ScriptSerializer
from . import lang_processor
from .models import Phrases, Script
from django.db import transaction
# celery tasks
from administrating.tasks import script_reporter
# python
import random
import string


class MessageAPIView(APIView):
    permission_classes = [AllowAny]
    message_serializer_class=MessageSerializer
    video_serializer=VideoSerializer
    default_phrase_processor = lang_processor.DefaultProcessor

    def post(self, request):
        serializer=self.message_serializer_class(context={'request':request}, data=request.data)
        if serializer.is_valid():
            scheme_pk= self.message_processor(serializer)
            print('SCHEME:', scheme_pk)
            try:
                validated_video_data=self.validate_video(data={'scheme_pk':scheme_pk})
                return Response(data=validated_video_data,status=201)
            except Exception as e:
                return Response(data={'error': str(e)}, status=400)
        else:
            return Response({'error': serializer.errors},status=400)

    def validate_video(self, data):
        serialized = self.video_serializer(data=data)
        if serialized.is_valid(raise_exception=True):
            return serialized.validated_data

    def message_processor(self, valid_serializer, commit_scheme=True):
        self.message_instance = valid_serializer.save()
        scheme_pk = self.default_phrase_processor().detect_scheme(text=self.message_instance.msg)
        if commit_scheme:
            self.message_instance.detected_scheme_id = scheme_pk
            self.message_instance.save()
        return scheme_pk


class GreetingAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class= VideoSerializer

    def get_queryset(self):
        return Phrases.objects.filter(topic='greeting').first()

    def get(self, request):
        greeting=self.get_queryset()
        serializer= self.serializer_class(data={'scheme_pk':greeting.pk})
        if serializer.is_valid():
            data=serializer.validated_data
            response=Response(data=data, status=200)
            response.set_cookie('anonimous_token', ''.join([random.choice(string.ascii_letters) for _ in range(25)]))
            return response
        return Response(data={'error':serializer.errors}, status=400)


class ScriptAPIView(MessageAPIView):
    default_phrase_processor = lang_processor.ScriptProcessor

    @staticmethod
    def validate_script(data):
        scripter = ScriptPositionSerializer(data=data)
        if scripter.is_valid(raise_exception=True):
            return scripter

    #@transaction.atomic
    def post(self, request):
        sid=transaction.savepoint()  # savepoint to rollback
        try:
            script_info=self.validate_script(data=request.data)
        except Exception as e:
            return Response(data={'error':str(e)}, status=404)
        message_serializer = self.message_serializer_class(context={'request':request}, data= request.data)
        if message_serializer.is_valid():
            # message created without scheme
            scheme_pk = self.message_processor(message_serializer, commit_scheme=False)
            # phrase detected with lang_processor
            phrase=Phrases.objects.get(pk=scheme_pk)
            print(scheme_pk, phrase)
            if phrase.topic != lang_processor.SCRIPT_ENDER:  # user wants to talk script
                try:
                    script_instance= Script.objects.get(pk=script_info.data['pk'])
                    # scheme related to script position
                    schemas=list(script_instance.script_related_phrases.all())[::-1]
                    scheme_pk=schemas[script_info.get_position()].pk
                    # saving scheme related to message
                    self.message_instance.detected_scheme_id=scheme_pk
                    self.message_instance.save()
                    # celery task if script ended
                    video_data = self.validate_video(data={'scheme_pk': scheme_pk})
                    if len(script_instance.script_related_phrases.all()) == script_info.get_position()+1:
                        transaction.on_commit(
                            lambda: self.make_celery_task(request.COOKIES.get('anonimous_token', None))
                        )
                        video_data.update({'script_end': True})
                    # send video
                    return Response(data=video_data, status=201)
                except Exception as e: # instance not found
                    transaction.savepoint_rollback(sid)  # something gone wrong
                    return Response(data={'error':str(e)}, status=404)
            else:  # user does not want to talk script
                # saving last answer
                self.message_instance.detected_scheme_id = scheme_pk
                self.message_instance.save()
                # making celery task
                transaction.on_commit(
                    lambda: self.make_celery_task(request.COOKIES.get('anonimous_token', None))
                )
                try:
                    video_data=self.validate_video(data={'scheme_pk':scheme_pk})
                    video_data.update({'script_end': True})
                    return Response(data=video_data, status=201)
                except:
                    return Response(data={'error': 'No video related to script-ending.','script_end':True},
                                    status=404)

    @staticmethod
    def make_celery_task(user_cookie):
        script_reporter.delay(user_cookie)
