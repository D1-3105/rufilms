from waitress import serve
from rufilms.wsgi import application
from rufilms.celery import app

if __name__ == '__main__':
    serve(application, host='localhost', port='8080', threads=10)