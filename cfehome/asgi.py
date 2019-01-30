import os 
import django
from channels.routing import get_default_application

#for production environment to use ASGI instead of WSGI
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cfehome.settings")
django.setup()
application = get_default_application