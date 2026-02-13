import os
from logging import getLogger

from django.core.wsgi import get_wsgi_application

from .conf import environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.base")

application = get_wsgi_application()

logger = getLogger(__name__)

logger.info("Using environment: %r", environment)
