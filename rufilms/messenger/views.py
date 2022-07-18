from rest_framework.views import APIView, Response
from rest_framework.permissions import AllowAny
from .serializers import MessageSerializer, VideoSerializer
from . import lang_processor
from .models import Phrases

class MessageView(APIView):
    permission_classes = [AllowAny]
    serializer_class=MessageSerializer
    video_serializer=VideoSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            scheme_pk=lang_processor.detect_scheme(serializer.data['msg'])
            print('SCHEME:', scheme_pk)
            serialized = self.video_serializer(data={'scheme_pk':scheme_pk})
            if serialized.is_valid():
                data=serialized.validated_data
                return Response(data=data,status=200)
            return Response(data={'error':'Something went wrong'}, status=400)
        else:
            return Response({'error':serializer.errors},status=400)



class GreetingView(APIView):
    permission_classes = [AllowAny]
    serializer_class= VideoSerializer

    def get_queryset(self):
        return Phrases.objects.filter(topic='greeting').first()

    def get(self, request):
        greeting=self.get_queryset()
        serializer= self.serializer_class(data={'scheme_pk':greeting.pk})
        if serializer.is_valid():
            data=serializer.validated_data
            return Response(data=data, status=200)
        return Response(data={'error':'Something went wrong'}, status=400)

# Create your views here.
