"""
URL configuration for web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from criticus.web import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("plain-text-to-json/", views.plain_text_to_json, name="txt2json"),
    path("md2tei/", views.markdown_to_tei, name="md2tei"),
    path("tei2json/", views.tei_to_json, name="tei2json"),
    path("tei2json/regex/add/", views.add_tei2json_regex, name="add-regex"),
    path(
        "tei2json/regex/<int:regex_pk>/", views.edit_tei2json_regex, name="edit-regex"
    ),
    path("combine-collations/", views.combine_collations, name="combine-collations"),
    path(
        "reformat-collation/",
        views.reformat_collation,
        name="reformat-collation",
    ),
    path("tei-viewer/", views.tei_viewer, name="tei-viewer"),
    path(
        "get-tei-transcription/",
        views.get_tei_transcription,
        name="get-tei-transcription",
    ),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
