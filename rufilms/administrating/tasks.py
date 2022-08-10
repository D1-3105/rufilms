# celery
from rufilms.celery import app
# local app
from .models import MailReceiver
from .serializers import ReadableMessageSerializer
# messenger app
from messenger.models import Message
from messenger.serializers import MessageSerializer
# django
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import get_template
# python
from datetime import datetime

def log(message, path='celery_log'):
    with open(path, 'a+') as l:
        time_info=datetime.now().strftime("%H:%M:%S - %m.%d.%Y")
        l.write(f'[{time_info}] - {message}\n')

@app.task
def script_reporter(user_cookie):
    db_messages=Message.objects.filter_new_messages().filter(anonimous_token=user_cookie)
    serialized_messages= MessageSerializer(db_messages, many=True).data
    readable_message_serializers=ReadableMessageSerializer(data=serialized_messages, many=True)
    readable_message_serializers.is_valid(raise_exception=True)
    readable_messages=readable_message_serializers.save()

    try:
        for receiver in MailReceiver.objects.all():
            html_template = get_template('administrating/%s_message.html' % receiver.message_language)
            context = {
                'messages': readable_messages,
                'passed_lang': receiver.message_language
            }

            html_content = html_template.render(context=context)

            try:
                result = send_mail(
                    'RuFilmsBot',
                    message=None,
                    from_email=settings.EMAIL_HOST_USER,
                    html_message=html_content,
                    recipient_list=[receiver.receiver_email]
                )
                log(f'SENT EMAIL TO:{receiver.receiver_email} RESULT WAS: {result}')
            except Exception as e:
                log(str(e))
    except Exception as e:
        log('FATAL: '+str(e))
        return 'Failure!'
    db_messages.update(reported=True)
    return 'Success!'
