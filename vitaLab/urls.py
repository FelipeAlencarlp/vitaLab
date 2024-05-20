from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('/auth/login/')),
    path('auth/', include('usuarios.urls')),
    path('exames/', include('exames.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
