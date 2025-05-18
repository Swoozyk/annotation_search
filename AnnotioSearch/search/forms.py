from django import forms
from django.core.exceptions import ValidationError
import os


class FileReplaceForm(forms.Form):
    new_file = forms.FileField(
        label='Выберите новый PDF-файл',
        help_text='Файл должен быть в формате PDF',
        widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    def clean_new_file(self):
        file = self.cleaned_data.get('new_file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            if ext != '.pdf':
                raise ValidationError("Допускаются только PDF-файлы")
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise ValidationError("Максимальный размер файла - 10 МБ")
        return file