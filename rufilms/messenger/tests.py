from rest_framework.test import APITestCase
from .views import MessageView


class MessageViewTesting(APITestCase):
    def setUp(self)->None:
        msg={
            'msg':'Как дела. Мне 20 лет, я Олег.'
        }



# Create your tests here.
