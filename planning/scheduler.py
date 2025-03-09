from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from ortools.sat.python import cp_model
from django.apps import apps

def generer_emploi_du_temps():
    """
    Génère automatiquement l’emploi du temps en respectant les disponibilités.
    """
    # Charger les modèles
    Matiere = apps.get_model('planning', 'Matiere')
    Enseignant = apps.get_model('planning', 'Enseignant')
    Groupe = apps.get_model('planning', 'Groupe')
    Affectation = apps.get_model('planning', 'Affectation')
    DisponibiliteEnseignant = apps.get_model('planning', 'DisponibiliteEnseignant')
    EmploiDuTemps = apps.get_model('planning', 'EmploiDuTemps')
    Salle = apps.get_model('planning', 'Salle')

    # Supprimer seulement les emplois futurs pour éviter la disparition totale
    EmploiDuTemps.objects.filter(date_heure__gte=datetime.now()).delete()  

    # Récupération des données
    affectations = list(Affectation.objects.all())
    disponibilites = {d.enseignant.id: d.date_heure for d in DisponibiliteEnseignant.objects.all()}
    salles = list(Salle.objects.all())

    # Jours et horaires disponibles
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    horaires = ["08:00", "10:00", "14:00", "16:00", "18:00"]
    date_debut = datetime.strptime("2025-03-10", "%Y-%m-%d")

    # Création du modèle OR-Tools
    model = cp_model.CpModel()
    emploi = {}

    # Variables de décision
    for affectation in affectations:
        for j, jour in enumerate(jours):
            for h, heure in enumerate(horaires):
                for salle in salles:  
                    emploi[(affectation.id, j, h, salle.id)] = model.NewBoolVar(f"{affectation.matiere.nom}_{affectation.groupe.nom}_{jour}_{heure}")

    # Contraintes : chaque affectation doit être placée sur 3 créneaux
    for affectation in affectations:
        model.Add(sum(emploi[(affectation.id, j, h, salle.id)] for j in range(len(jours)) for h in range(len(horaires)) for salle in salles) == 3)

    # Contrainte : Un enseignant ne peut pas être affecté à deux cours en même temps
    for enseignant in Enseignant.objects.all():
        for j, jour in enumerate(jours):
            for h, heure in enumerate(horaires):
                model.Add(sum(emploi[(a.id, j, h, salle.id)] for a in affectations if a.enseignant == enseignant for salle in salles) <= 1)

    # Contraintes : Respect des disponibilités des enseignants
    for affectation in affectations:
        if affectation.enseignant.id in disponibilites:
            dispo_date = disponibilites[affectation.enseignant.id]
            jour_index = (dispo_date.weekday()) % len(jours)
            heure_index = horaires.index(dispo_date.strftime("%H:%M"))
            for salle in salles:
                model.Add(emploi[(affectation.id, jour_index, heure_index, salle.id)] == 1)

    # Résolution du problème
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Sauvegarde dans la base de données
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        for (affectation_id, j, h, salle_id), var in emploi.items():
            if solver.Value(var) == 1:
                affectation = Affectation.objects.get(id=affectation_id)
                salle = Salle.objects.get(id=salle_id)
                date_heure = date_debut + timedelta(days=j)
                date_heure = make_aware(datetime.strptime(f"{date_heure.date()} {horaires[h]}", "%Y-%m-%d %H:%M"))

                EmploiDuTemps.objects.create(
                    groupe=affectation.groupe,
                    enseignant=affectation.enseignant,
                    matiere=affectation.matiere,
                    salle=salle,
                    date_heure=date_heure
                )

        print("✅ Emploi du temps généré avec succès.")
    else:
        print("❌ Aucune solution trouvée.")
