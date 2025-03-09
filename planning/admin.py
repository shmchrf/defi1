from django.contrib import admin
from .models import *

admin.site.register(Matiere)
admin.site.register(Enseignant)
admin.site.register(Groupe)
admin.site.register(DisponibiliteEnseignant)
admin.site.register(EmploiDuTemps)