from django import forms
from .models import *

class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['code', 'nom', 'credits', 'semestre', 'filiere']

class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = ['nom', 'identifiant']

class GroupeForm(forms.ModelForm):
    class Meta:
        model = Groupe
        fields = ['nom', 'semestre', 'parent_groupe']

class DisponibiliteForm(forms.ModelForm):
    class Meta:
        model = DisponibiliteEnseignant
        fields = ['enseignant', 'jour', 'creneau']