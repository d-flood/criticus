from django.db import models


class Settings(models.Model):
    name = models.CharField(max_length=255, unique=True)
    txt2json_input_dir = models.CharField(max_length=255, default="", blank=True)
    txt2json_output_dir = models.CharField(max_length=255, default="", blank=True)
    md2tei_input_dir = models.CharField(max_length=255, default="", blank=True)
    md2tei_output_dir = models.CharField(max_length=255, default="", blank=True)
    tei2json_input_dir = models.CharField(max_length=255, default="", blank=True)
    tei2json_output_dir = models.CharField(max_length=255, default="", blank=True)
    combine_collations_input_dir = models.CharField(
        max_length=255, default="", blank=True
    )
    combine_collations_output_file = models.CharField(
        max_length=255, default="", blank=True
    )
    combine_collations_startswith = models.CharField(
        max_length=255, default="", blank=True
    )
    combine_collations_title_stmt = models.CharField(
        max_length=255, default="", blank=True
    )
    combine_collations_publication_stmt = models.CharField(
        max_length=255, default="", blank=True
    )
    reformat_collation_input_file = models.CharField(
        max_length=255, default="", blank=True
    )
    reformat_collation_output_file = models.CharField(
        max_length=255, default="", blank=True
    )
    reformat_collation_title_stmt = models.CharField(
        max_length=255, default="", blank=True
    )
    reformat_collation_publication_stmt = models.CharField(
        max_length=255, default="", blank=True
    )
    tei_viewer_input_dir = models.CharField(max_length=255, default="", blank=True)

    tei2json_regexes: models.QuerySet["CustomRegex"]

    class Meta:
        verbose_name_plural = "Settings"
        app_label = "web"


class CustomRegex(models.Model):
    settings = models.ForeignKey(
        Settings, on_delete=models.CASCADE, related_name="tei2json_regexes"
    )
    active = models.BooleanField(default=True)
    expression = models.CharField(max_length=255)
    replacement = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Custom Regexes"
        app_label = "web"
