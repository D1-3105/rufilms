import subprocess

REDIS_HOST='redis'
REDIS_PORT=6379
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
# CELERY_BIN = "/home/user/.virtualenvs/venv/bin/celery"
CELERY_BROKER_URL='redis://localhost:6379/0'
CELERY_RESULT_BACKEND='redis://localhost:6379/0'
CELERY_BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler'
CELERYD_CHDIR=r"D:\Projects\rufilms\rufilms"
#
CELERYD_OPTS="--time-limit=300 --concurrency=8"
#
CELERYD_LOG_FILE= '/celery.log'
# Workers should run as an unprivileged user.
#   You need to create this user manually (or you can choose
#   a user/group combination that already exists (e.g., nobody).
# CELERYD_USER="celery"
# CELERYD_GROUP="celery"
CELERYD_LOG_LEVEL="INFO"
# If enabled PID and log directories will be created if missing,
# and owned by the userid/group configured.
CELERY_CREATE_DIRS=1

# CELERY WORKER INITIALIZING
#celery_worker_process= subprocess.Popen('python /rufilms/manage.py celery worker -Q low -c 2 & '
#                                        'python /rufilms/manage.py celery beat')
#celery_debug_worker.communicate()
print('INITIALIZED!')