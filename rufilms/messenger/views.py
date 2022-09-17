# rest
from rest_framework.views import APIView, Response
from rest_framework.permissions import AllowAny ,BasePermission
# local
from .serializers import MessageSerializer, VideoSerializer, ScriptPositionSerializer, SenderSerializer
from . import lang_processor
from .models import Phrases, Script, Sender
from django.db import transaction
from django.db.models import QuerySet
# celery tasks
from administrating.tasks import script_reporter
# python
import random
import string


class CookiePermission(BasePermission):

    def has_permission(self, request, view):
        tok = request.COOKIES.get('anonimous_token')
        return tok and Sender.objects.filter(anonimous_token=tok).exists()


class VideoAPIView(APIView):
    video_serializer = VideoSerializer
    phrase_topic=''

    def get(self, request):
        print('CALLED '+self.phrase_topic)
        scheme_pk = Phrases.objects.get(topic=self.phrase_topic).pk
        try:
            validated_data = self.validate_video({'scheme_pk': scheme_pk})
            return Response(data=validated_data, status=200)
        except Exception as e:
            print(e)
            return Response(status=404)

    def validate_video(self, data):
        serialized = self.video_serializer(data=data)
        if serialized.is_valid(raise_exception=True):
            return serialized.validated_data


class IntroductionAPIView(VideoAPIView):
    permission_classes = [AllowAny]
    phrase_topic = 'INTRODUCTION'


class AuthAPIView(VideoAPIView):
    permission_classes = [AllowAny]
    serializer_class= SenderSerializer
    phrase_topic = 'AUTH PHRASE'

    @staticmethod
    def make_anon_cookie():
        return ''.join([random.choice(string.ascii_letters) for _ in range(25)])

    def post(self, request, format=None):
        anon_cookie=self.make_anon_cookie()
        data=request.data.copy()
        data.update({'anonimous_token':anon_cookie})
        print('DATA:', data)
        ser_inited=self.serializer_class(data=data)

        if ser_inited.is_valid():
            sender_instance=ser_inited.save()
            response=Response(status=201)
            response.set_cookie('anonimous_token', anon_cookie)
            return response
        else:
            return Response(data={'error':ser_inited.errors}, status=400)

    def get(self, request):
        return super().get(request)


class GreetingAPIView(VideoAPIView):
    permission_classes = [CookiePermission]
    phrase_topic = 'greeting'


class MessageAPIView(APIView):
    permission_classes = [CookiePermission]
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
                print(e)
                return Response(data={'error': str(e)}, status=400)
        else:
            print(serializer.errors)
            return Response({'error': serializer.errors},status=400)

    def validate_video(self, data):
        serialized = self.video_serializer(data=data)
        if serialized.is_valid(raise_exception=True):
            return serialized.validated_data

    def message_processor(self, valid_serializer, commit_scheme=True, commit=True):
        if commit:
            self.message_instance = valid_serializer.save()
        scheme_pk = self.default_phrase_processor().detect_scheme(text=self.message_instance.msg)
        if commit_scheme:
            self.message_instance.detected_scheme_id = scheme_pk
            self.message_instance.save()
        return scheme_pk


class ScriptAPIView(MessageAPIView):
    default_phrase_processor = lang_processor.ScriptProcessor

    @staticmethod
    def validate_script(data):
        scripter = ScriptPositionSerializer(data=data)
        if scripter.is_valid(raise_exception=True):
            return scripter

    @staticmethod
    def make_script_list(phrases_list):
        for script in Script.objects.all():
            if list(script.sort_phrases_by_topic())[:len(phrases_list)] == phrases_list:
                yield script

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
            #
            make_script_phrases_list = lambda scripted: list(scripted.sort_phrases_by_topic())
            print(scheme_pk, phrase)
            if phrase.topic != lang_processor.SCRIPT_ENDER:  # user wants to talk script
                #
                try:
                    script_instance = Script.objects.get(pk=script_info.data['pk'])
                    # scheme related to script position
                    schemas = make_script_phrases_list(script_instance)
                    script_list = list(self.make_script_list(schemas[:script_info.data['position']]))
                    #
                    print('HERE SCRIPT LIST',script_list)
                    script_pos = script_info.get_position()
                    #
                    change_script = None
                    if len(script_list) > 1:
                        phrases_list = []
                        for script in script_list:
                            phrases_list.append(
                                make_script_phrases_list(script)[script_pos].pk
                            )

                        print(request.data['msg'],phrases_list)
                        branch_pk = lang_processor.ScriptCustomProcessor(phrases_list). \
                            detect_scheme(text=self.message_instance.msg)

                        if branch_pk in phrases_list:
                            script_instance = script_list[phrases_list.index(branch_pk)]
                            change_script = script_instance.pk
                            schemas = make_script_phrases_list(script_instance)

                    print('SCHEMAS',schemas)

                    scheme_pk = schemas[script_pos].pk
                    # saving scheme related to message
                    self.message_instance.detected_scheme_id=scheme_pk
                    self.message_instance.save()
                    # celery task if script ended
                    video_data = self.validate_video(data={'scheme_pk': scheme_pk})
                    #print('NEXT',make_script_phrases_list(script_instance)[script_info.get_position()+1].topic)
                    if len(script_instance.script_related_phrases.all()) == script_pos + 1 or \
                            make_script_phrases_list(script_instance)[script_pos].topic == lang_processor.SCRIPT_ENDER:
                        transaction.on_commit(
                            lambda: self.make_celery_task(request.COOKIES.get('anonimous_token', None))
                        )
                        video_data.update({'script_end': True})
                    if change_script:
                        video_data.update({'change_script':change_script})
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

