from django.db import models


class Settings(models.Model):
    name = models.CharField(max_length=255, unique=True)
    txt2json_input_dir = models.CharField(max_length=255, default="", blank=True)
    txt2json_output_dir = models.CharField(max_length=255, default="", blank=True)
    md2tei_input_dir = models.CharField(max_length=255, default="", blank=True)
    md2tei_output_dir = models.CharField(max_length=255, default="", blank=True)
    tei2json_input_dir = models.CharField(max_length=255, default="", blank=True)
    tei2json_output_dir = models.CharField(max_length=255, default="", blank=True)
    tei2json_active_regex = models.JSONField(default=list)
    tei2json_inactive_regex = models.JSONField(default=list)

    class Meta:
        verbose_name_plural = "Settings"

    def __str__(self):
        return self.key
