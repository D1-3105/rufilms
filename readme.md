# rufilms/rufilms/.env
RUFILMS_CORS_ALLOWED_ORIGINS=http://localhost:3000,https://localhost:3000,https://localhost:8000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,https://localhost:8080,localhost
RUFILMS_CSRF_TRUSTED_ORIGINS=http://localhost:3000,https://localhost:3000,https://localhost:8000,http://localhost:8000,http://127.0.0.1:8000,https://localhost:8080,localhost
RUFILMS_ALLOWED_HOSTS=https://localhost:8000,http://localhost:8000,http://127.0.0.1:8000,http://localhost:8080,https://localhost:8080,http://127.0.0.1:8080,localhost
RUFILMS_DEBUG=False
##### ADD RUFILMS_FFMPEG_PATH
##### To launch celery in test mode windows: celery -A rufilms worker -l info -P gevent
##### To launch redis server in windows: redis-server --port 6379