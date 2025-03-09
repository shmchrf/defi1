from rest_framework import serializers
from .models import *

class MatiereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Matiere
        fields = '__all__'

class EnseignantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enseignant
        fields = '__all__'

class GroupeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groupe
        fields = '__all__'

class EmploiDuTempsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploiDuTemps
        fields = '__all__'
