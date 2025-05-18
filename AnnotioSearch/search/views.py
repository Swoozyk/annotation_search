import os
from django.shortcuts import render
from .utils import search_documents
from django.http import FileResponse
from django.conf import settings
from django.http import Http404
from .models import Documents
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import FileReplaceForm
from django.contrib.auth.decorators import user_passes_test
from django.core.files.storage import default_storage
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def disciplines_main(request):
    # Получаем список всех факультетов
    faculties = Documents.objects.values_list('faculty', flat=True).distinct()
    return render(request, 'search/disciplines_main.html', {'faculties': faculties})


def disciplines_by_faculty(request, faculty):
    # Получаем уровни образования для выбранного факультета
    levels = Documents.objects.filter(faculty=faculty).values_list('education_level', flat=True).distinct()
    return render(request, 'search/disciplines_by_faculty.html', {
        'faculty': faculty,
        'levels': levels
    })


def disciplines_by_level(request, faculty, education_level):
    # Получаем года поступления для выбранного факультета и уровня
    years = Documents.objects.filter(
        faculty=faculty,
        education_level=education_level
    ).values_list('admission_year', flat=True).distinct().order_by('-admission_year')

    return render(request, 'search/disciplines_by_level.html', {
        'faculty': faculty,
        'education_level': education_level,
        'years': years
    })


def disciplines_by_year(request, faculty, education_level, year):
    # Получаем направления подготовки для выбранных параметров
    fields = Documents.objects.filter(
        faculty=faculty,
        education_level=education_level,
        admission_year=year
    ).values_list('study_field', flat=True).distinct()

    return render(request, 'search/disciplines_by_year.html', {
        'faculty': faculty,
        'education_level': education_level,
        'year': year,
        'fields': fields
    })


def disciplines_by_field(request, faculty, education_level, year, study_field):
    # Получаем список аннотаций для выбранных параметров
    annotations = Documents.objects.filter(
        faculty=faculty,
        education_level=education_level,
        admission_year=year,
        study_field=study_field
    )
    for annotation in annotations:
        annotation.file_path = annotation.file_path.replace('\\', '/')
    return render(request, 'search/disciplines_by_field.html', {
        'faculty': faculty,
        'education_level': education_level,
        'year': year,
        'study_field': study_field,
        'annotations': annotations
    })

def pdf_view(request, file_path):
    """Открывает PDF в браузере"""
    return serve_pdf(request, file_path, disposition='inline')


def pdf_download(request, file_path):
    """Скачивает PDF"""
    return serve_pdf(request, file_path, disposition='attachment')


def serve_pdf(request, file_path, disposition):
    """Общая функция для работы с PDF"""
    # Безопасная обработка пути
    file_path = os.path.normpath(file_path)
    if '..' in file_path or file_path.startswith('/'):
        raise Http404("Недопустимый путь")

    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if os.path.exists(full_path):
        response = FileResponse(open(full_path, 'rb'))
        response['Content-Type'] = 'application/pdf'
        response['Content-Disposition'] = f'{disposition}; filename="{os.path.basename(file_path)}"'
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    else:
        raise Http404("Файл не найден")


@login_required
def index(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = search_documents(query)

    return render(request, 'search/index.html', {
        'query': query,
        'results': results
    })


def editor_check(user):
    return user.groups.filter(name='Редакторы').exists() or user.is_superuser


@user_passes_test(editor_check, login_url='/login/')
def replace_file(request, doc_id):
    document = get_object_or_404(Documents, id=doc_id)

    if request.method == 'POST':
        form = FileReplaceForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Удаляем старый файл
                if default_storage.exists(document.file_path):
                    default_storage.delete(document.file_path)

                # Сохраняем новый файл под тем же путем
                default_storage.save(document.file_path, form.cleaned_data['new_file'])

                return redirect('disciplines_by_field',
                                faculty=document.faculty,
                                education_level=document.education_level,
                                year=document.admission_year,
                                study_field=document.study_field)

            except Exception as e:
                return render(request, 'error.html', {
                    'error': f'Ошибка замены файла: {str(e)}'
                })

    else:
        form = FileReplaceForm()

    return render(request, 'search/replace_file.html', {
        'form': form,
        'document': document
    })


@user_passes_test(editor_check, login_url='/login/')
def delete_document(request, doc_id):
    document = get_object_or_404(Documents, id=doc_id)

    if request.method == 'POST':
        try:
            # Удаление файла
            if default_storage.exists(document.file_path):
                default_storage.delete(document.file_path)

            # Удаление записи
            document.delete()
            messages.success(request, 'Документ успешно удален')
            return redirect('disciplines_main')

        except Exception as e:
            messages.error(request, f'Ошибка удаления: {str(e)}')
            return redirect('disciplines_by_field',
                            faculty=document.faculty,
                            education_level=document.education_level,
                            year=document.admission_year,
                            study_field=document.study_field)

    return render(request, 'confirm_delete.html', {'document': document})
