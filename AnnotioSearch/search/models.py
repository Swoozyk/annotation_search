# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Documents(models.Model):
    file_name = models.TextField(verbose_name="Название файла")
    file_path = models.TextField(unique=True, verbose_name="Путь к файлу")
    content = models.TextField(blank=True, null=True, verbose_name="Содержимое")
    tsv = models.TextField(blank=True, null=True, verbose_name="TSVECTOR")

    faculty = models.TextField(verbose_name="Факультет")
    education_level = models.CharField(
        max_length=20,
        verbose_name="Уровень образования",
        choices=[
            ('bachelor', 'Бакалавриат'),
            ('master', 'Магистратура'),
            ('phd', 'Аспирантура')
        ]
    )
    admission_year = models.IntegerField(verbose_name="Год поступления")
    study_field = models.TextField(verbose_name="Направление подготовки")

    class Meta:
        managed = False
        db_table = 'documents_2'
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        indexes = [
            models.Index(fields=['faculty']),
            models.Index(fields=['education_level']),
            models.Index(fields=['admission_year']),
            models.Index(fields=['study_field']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.get_education_level_display()})"
