import logging
import sys
from pathlib import Path

import django
from django import conf, urls
from django.conf.urls.static import static
from django.core.handlers import asgi

from criticus import views

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

logger.debug("Starting application setup...")

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

conf.settings.configure(
    SECRET_KEY="not-important-in-this-context",
    DEBUG=True,
    ALLOWED_HOSTS="*",
    ROOT_URLCONF=__name__,
    STATIC_URL="/static/",
    STATICFILES_DIRS=[
        BASE_DIR / "static",
    ],
    INSTALLED_APPS=[
        "django.contrib.staticfiles",
    ],
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [TEMPLATES_DIR],
            "OPTIONS": {
                "loaders": [
                    ("django.template.loaders.filesystem.Loader", [TEMPLATES_DIR])
                ],
            },
        }
    ],
)

try:
    django.setup()
    logger.info("Django setup completed successfully")
except Exception as e:
    logger.error(f"Failed to setup Django: {e}", exc_info=True)
    raise

app = asgi.ASGIHandler()


urlpatterns = [
    urls.path("", views.home, name="home"),
    urls.path("plain-text-to-json/", views.plain_text_to_json, name="txt2json"),
    urls.path("md2tei/", views.markdown_to_tei, name="md2tei"),
]

urlpatterns += static(conf.settings.STATIC_URL, document_root=BASE_DIR / "static")

# Export the ASGI application
application = app

logger.debug("Application setup completed")
