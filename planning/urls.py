from django.urls import path
from .views import *

urlpatterns = [
    path('', afficher_accueil, name='accueil'),
    path('matieres/', afficher_matieres, name='matieres'),
    path('enseignants/', afficher_enseignants, name='enseignants'),
    path('affectations/', afficher_affectations, name='affectations'),
    path('groupes/', afficher_groupes, name='groupes'),
    path('emploi/', afficher_emploi_du_temps, name='emploi_du_temps'),
    path('planifier/', planifier, name='planifier'),
    path('dashboard/', afficher_dashboard, name='dashboard'),

    # Routes AJAX
    path('ajouter_matiere/', ajouter_matiere, name='ajouter_matiere'),
    path('modifier_matiere/', modifier_matiere, name='modifier_matiere'),
    path('supprimer_matiere/', supprimer_matiere, name='supprimer_matiere'),

    path('ajouter_enseignant/', ajouter_enseignant, name='ajouter_enseignant'),
    path('modifier_enseignant/', modifier_enseignant, name='modifier_enseignant'),
    path('supprimer_enseignant/', supprimer_enseignant, name='supprimer_enseignant'),

    path('ajouter_groupe/', ajouter_groupe, name='ajouter_groupe'),
    path('modifier_groupe/', modifier_groupe, name='modifier_groupe'),
    path('supprimer_groupe/', supprimer_groupe, name='supprimer_groupe'),

    # Exportation
    path('export/excel/', exporter_emploi_excel, name='exporter_emploi_excel'),
    path('export/pdf/', exporter_emploi_pdf, name='exporter_emploi_pdf'),

    path('ajouter_disponibilite/', ajouter_disponibilite, name='ajouter_disponibilite'),
    path('modifier_disponibilite/', modifier_disponibilite, name='modifier_disponibilite'),
    # path('supprimer_disponibilite/', supprimer_disponibilite, name='supprimer_disponibilite'),

    path('ajouter_sous_groupe/', ajouter_sous_groupe, name='ajouter_sous_groupe'),
    path('modifier_sous_groupe/', modifier_sous_groupe, name='modifier_sous_groupe'),
    path('supprimer_sous_groupe/', supprimer_sous_groupe, name='supprimer_sous_groupe'),

    path('ajouter_affectation/', ajouter_affectation, name='ajouter_affectation'),
    path('supprimer_affectation/', supprimer_affectation, name='supprimer_affectation'),

    path('salles/', afficher_salles, name='salles'),
    path('ajouter_salle/', ajouter_salle, name='ajouter_salle'),
    path('modifier_salle/', modifier_salle, name='modifier_salle'),
    path('supprimer_salle/', supprimer_salle, name='supprimer_salle'),

    # path('generer_emploi_du_temps/', generer_emploi_du_temps_view, name='generer_emploi_du_temps'),

    path('planifier/', planifier_emploi_du_temps, name='planifier_emploi_du_temps'),

]
