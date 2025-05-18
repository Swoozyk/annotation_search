"""
URL configuration for AnnotioSearch project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from search import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/')),
    path('login/', auth_views.LoginView.as_view(
        template_name='search/authentication.html',
        redirect_authenticated_user=False,
        extra_context={'title': 'Авторизация'}
    ), name='login'),
    path('search/', views.index, name='index'),
    path('disciplines/', views.disciplines_main, name='disciplines_main'),
    path('disciplines/<str:faculty>/', views.disciplines_by_faculty, name='disciplines_by_faculty'),
    path('disciplines/<str:faculty>/<str:education_level>/', views.disciplines_by_level, name='disciplines_by_level'),
    path('disciplines/<str:faculty>/<str:education_level>/<int:year>/', views.disciplines_by_year, name='disciplines_by_year'),
    path('disciplines/<str:faculty>/<str:education_level>/<int:year>/<str:study_field>/', views.disciplines_by_field, name='disciplines_by_field'),
    path('view/<path:file_path>', views.pdf_view, name='pdf_view'),
    path('download/<path:file_path>', views.pdf_download, name='pdf_download'),
    path('replace/<int:doc_id>/', views.replace_file, name='replace_file'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete_document'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
