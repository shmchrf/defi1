from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Accès à l'admin Django
    path('', include('planning.urls')),  # Inclusion des routes de ton application principale
]
