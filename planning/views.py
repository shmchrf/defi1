import io
import json
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import *
from .scheduler import generer_emploi_du_temps
from django.shortcuts import get_object_or_404
from datetime import datetime
from ortools.sat.python import cp_model

from ortools.sat.python import cp_model
from django.utils.timezone import make_aware
from datetime import datetime, timedelta


from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver


def afficher_accueil(request):
    return render(request, "planning/base.html")

def afficher_matieres(request):
    matieres = Matiere.objects.all()
    return render(request, "planning/matieres.html", {"matieres": matieres})

def afficher_enseignants(request):
    enseignants = Enseignant.objects.all()
    return render(request, "planning/enseignants.html", {"enseignants": enseignants})

def afficher_affectations(request):
    enseignants = Enseignant.objects.all()
    matieres = Matiere.objects.all()
    groupes = Groupe.objects.all()
    affectations = Affectation.objects.all()

    return render(request, "planning/affectations.html", {
        "enseignants": enseignants,
        "matieres": matieres,
        "groupes": groupes,
        "affectations": affectations
    })

def afficher_groupes(request):
    groupes = Groupe.objects.all()
    return render(request, "planning/groupes.html", {"groupes": groupes})



#  Gestion des Matières
@csrf_exempt
def ajouter_matiere(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        matiere = Matiere.objects.create(
            code=data['code'],
            nom=data['nom'],
            credits=int(data['credits']),
            semestre=int(data['semestre']),
            filiere=data['filiere']
        )
        return JsonResponse({'message': 'Matière ajoutée avec succès', 'id': matiere.id})

@csrf_exempt
def modifier_matiere(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        matiere = Matiere.objects.get(id=data['id'])
        matiere.code = data['code']
        matiere.nom = data['nom']
        matiere.credits = int(data['credits'])
        matiere.semestre = int(data['semestre'])
        matiere.filiere = data['filiere']
        matiere.save()
        return JsonResponse({'message': 'Matière modifiée avec succès'})

@csrf_exempt
def supprimer_matiere(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Matiere.objects.get(id=data['id']).delete()
        return JsonResponse({'message': 'Matière supprimée avec succès'})

#  Gestion des Enseignants
@csrf_exempt
def ajouter_enseignant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enseignant = Enseignant.objects.create(
            nom=data['nom'],
            disponibilites=data.get('disponibilites', {})
        )
        return JsonResponse({'message': 'Enseignant ajouté avec succès', 'id': enseignant.id})

@csrf_exempt
def modifier_enseignant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        enseignant = Enseignant.objects.get(id=data['id'])
        enseignant.nom = data['nom']
        enseignant.disponibilites = data.get('disponibilites', {})
        enseignant.save()
        return JsonResponse({'message': 'Enseignant modifié avec succès'})

@csrf_exempt
def supprimer_enseignant(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Enseignant.objects.get(id=data['id']).delete()
        return JsonResponse({'message': 'Enseignant supprimé avec succès'})

#  Gestion des Groupes
@csrf_exempt
def ajouter_groupe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        groupe = Groupe.objects.create(
            nom=data['nom'],
            semestre=int(data['semestre']),
            parent_groupe_id=data.get('parent_groupe_id')
        )
        return JsonResponse({'message': 'Groupe ajouté avec succès', 'id': groupe.id})

@csrf_exempt
def modifier_groupe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        groupe = Groupe.objects.get(id=data['id'])
        groupe.nom = data['nom']
        groupe.semestre = int(data['semestre'])
        groupe.parent_groupe_id = data.get('parent_groupe_id')
        groupe.save()
        return JsonResponse({'message': 'Groupe modifié avec succès'})

@csrf_exempt
def supprimer_groupe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Groupe.objects.get(id=data['id']).delete()
        return JsonResponse({'message': 'Groupe supprimé avec succès'})





# Export en PDF
def exporter_emploi_pdf(request):
    emplois = EmploiDuTemps.objects.all()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="emploi_du_temps.pdf"'

    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle("Emploi du Temps")

    pdf.drawString(200, 750, "Emploi du Temps")

    y_position = 720
    pdf.drawString(50, y_position, "Groupe | Enseignant | Matière | Salle | Date & Heure")
    y_position -= 20

    for emploi in emplois:
        pdf.drawString(50, y_position, f"{emploi.groupe.nom} | {emploi.enseignant.nom} | {emploi.matiere.nom} | {emploi.salle.nom if emploi.salle else 'Non attribuée'} | {emploi.date_heure}")
        y_position -= 20

    pdf.save()
    return response

def exporter_emploi_excel(request):
    emplois = EmploiDuTemps.objects.all()
    data = []

    for emploi in emplois:
        data.append({
            "Groupe": emploi.groupe.nom,
            "Enseignant": emploi.enseignant.nom,
            "Matière": emploi.matiere.nom,
            "Salle": emploi.salle.nom if emploi.salle else 'Non attribuée',
            "Date & Heure": emploi.date_heure
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Emploi du Temps", index=False)

    output.seek(0)
    response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="emploi_du_temps.xlsx"'

    return response


@csrf_exempt
def ajouter_disponibilite(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Vérifier si enseignant_id est bien présent et valide
            if not data.get('enseignant_id'):
                return JsonResponse({'error': 'enseignant_id est requis'}, status=400)

            try:
                enseignant = Enseignant.objects.get(id=data['enseignant_id'])
            except Enseignant.DoesNotExist:
                return JsonResponse({'error': 'Enseignant non trouvé'}, status=404)

            # Vérifier si la date est bien formatée
            try:
                date_heure = datetime.strptime(data['date_heure'], "%Y-%m-%dT%H:%M")
            except ValueError:
                return JsonResponse({'error': 'Format de date incorrect. Utilisez YYYY-MM-DDTHH:MM'}, status=400)

            disponibilite = DisponibiliteEnseignant.objects.create(
                enseignant=enseignant,
                date_heure=date_heure
            )

            return JsonResponse({'message': 'Disponibilité ajoutée avec succès', 'id': disponibilite.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def modifier_disponibilite(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            disponibilite = get_object_or_404(DisponibiliteEnseignant, id=data['id'])
            
            disponibilite.date_heure = data['date_heure']
            disponibilite.save()

            return JsonResponse({'message': 'Disponibilité modifiée avec succès'})
        except DisponibiliteEnseignant.DoesNotExist:
            return JsonResponse({'error': 'Disponibilité non trouvée'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def ajouter_sous_groupe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            groupe_parent = Groupe.objects.get(id=data['parent_groupe_id'])
            sous_groupe = Groupe.objects.create(
                nom=data['nom'],
                semestre=groupe_parent.semestre,
                parent_groupe=groupe_parent
            )
            return JsonResponse({'message': 'Sous-groupe ajouté avec succès', 'id': sous_groupe.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def modifier_sous_groupe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sous_groupe = Groupe.objects.get(id=data['id'])
            sous_groupe.nom = data['nom']
            sous_groupe.save()
            return JsonResponse({'message': 'Sous-groupe modifié avec succès'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def supprimer_sous_groupe(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Groupe.objects.get(id=data['id']).delete()
            return JsonResponse({'message': 'Sous-groupe supprimé avec succès'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




@receiver(post_save, sender=Enseignant)
@receiver(post_save, sender=Groupe)
@receiver(post_save, sender=Matiere)
def maj_emploi_du_temps(sender, instance, **kwargs):
    generer_emploi_du_temps()

@receiver(post_save, sender=Affectation)
@receiver(post_save, sender=Matiere)
@receiver(post_save, sender=Enseignant)
@receiver(post_save, sender=Groupe)
@receiver(post_delete, sender=Affectation)
@receiver(post_delete, sender=Matiere)
@receiver(post_delete, sender=Enseignant)
@receiver(post_delete, sender=Groupe)
def mise_a_jour_emploi_du_temps(sender, instance, **kwargs):
    print("🔄 Mise à jour détectée, régénération de l'emploi du temps...")
    generer_emploi_du_temps()


def planifier(request):
    resultat = generer_emploi_du_temps()
    return JsonResponse({"message": resultat})

# === EXPORTATION PDF & EXCEL ===
def exporter_emploi_pdf(request):
    emplois = EmploiDuTemps.objects.all()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="emploi_du_temps.pdf"'
    pdf = canvas.Canvas(response, pagesize=letter)
    pdf.setTitle("Emploi du Temps")
    pdf.drawString(200, 750, "Emploi du Temps")
    y_position = 720
    pdf.drawString(50, y_position, "Groupe | Enseignant | Matière | Salle | Date & Heure")
    y_position -= 20
    for emploi in emplois:
        pdf.drawString(50, y_position, f"{emploi.groupe.nom} | {emploi.enseignant.nom} | {emploi.matiere.nom} | {emploi.salle.nom if emploi.salle else 'Non attribuée'} | {emploi.date_heure}")
        y_position -= 20
    pdf.save()
    return response

def exporter_emploi_excel(request):
    emplois = EmploiDuTemps.objects.all()
    data = [{
        "Groupe": emploi.groupe.nom,
        "Enseignant": emploi.enseignant.nom,
        "Matière": emploi.matiere.nom,
        "Salle": emploi.salle.nom if emploi.salle else 'Non attribuée',
        "Date & Heure": emploi.date_heure
    } for emploi in emplois]
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Emploi du Temps", index=False)
    output.seek(0)
    response = HttpResponse(output, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="emploi_du_temps.xlsx"'
    return response

# === PLANIFICATEUR OR-TOOLS ===
# from django.utils.timezone import make_aware
# from datetime import datetime, timedelta
# from ortools.sat.python import cp_model
from django.apps import apps



# from ortools.sat.python import cp_model
# from django.utils.timezone import make_aware
# from datetime import datetime
# from .models import EmploiDuTemps, Affectation, Salle, Enseignant, Matiere, DisponibiliteEnseignant

# def generer_emploi_du_temps():
#     model = cp_model.CpModel()

#     # Get all necessary data
#     matieres = list(Matiere.objects.all())
#     enseignants = list(Enseignant.objects.all())
#     groupes = list(Groupe.objects.all())
#     salles = list(Salle.objects.all())
#     affectations = list(Affectation.objects.all())
    
#     # Availability of teachers (mapping of teacher ID to available times)
#     disponibilites = {
#         dispo.enseignant.id: dispo.date_heure for dispo in DisponibiliteEnseignant.objects.all()
#     }
    
#     jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
#     plages_horaires = [8, 10, 12, 14, 16]  # Fixed available hours: 8am, 10am, 12pm, 2pm, 4pm

#     emploi = {}

#     # Create decision variables for each possible class-time combination
#     for affectation in affectations:
#         for salle in salles:
#             for jour in range(len(jours)):
#                 for plage in plages_horaires:
#                     emploi[(affectation.id, salle.id, jour, plage)] = model.NewBoolVar(
#                         f"{affectation.matiere.nom}_{affectation.enseignant.nom}_{affectation.groupe.nom}_{salle.nom}_{jours[jour]}_{plage}"
#                     )

#     # Constraints
#     for affectation in affectations:
#         for salle in salles:
#             for jour in range(len(jours)):
#                 for plage in plages_horaires:
#                     # Check if the teacher is available at this time
#                     enseignant = affectation.enseignant
#                     if enseignant.id in disponibilites:
#                         # Get teacher availability for this teacher
#                         dispo_date = disponibilites[enseignant.id]
#                         # We assume availability is provided in a form like "2025-03-10 10:00:00"
#                         if dispo_date.strftime("%A") == jours[jour] and dispo_date.hour == plage:
#                             # Teacher is available at this time, so we allow this combination
#                             pass
#                         else:
#                             # Teacher is not available at this time, we add the constraint to block this slot
#                             model.Add(emploi[(affectation.id, salle.id, jour, plage)] == 0)

#     # Solve the model
#     solver = cp_model.CpSolver()
#     status = solver.Solve(model)

#     if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
#         EmploiDuTemps.objects.all().delete()  # Clear previous schedule

#         # Create the schedule based on the solution
#         for (affectation_id, salle_id, jour, plage), var in emploi.items():
#             if solver.Value(var) == 1:
#                 affectation = Affectation.objects.get(id=affectation_id)
#                 salle = Salle.objects.get(id=salle_id)
#                 date_heure = datetime.strptime(f"{jours[jour]} {plage}:00", "%A %H:%M:%S")
#                 date_heure = make_aware(date_heure)

#                 # Save the valid schedule to the database
#                 EmploiDuTemps.objects.create(
#                     groupe=affectation.groupe,
#                     enseignant=affectation.enseignant,
#                     matiere=affectation.matiere,
#                     salle=salle,
#                     date_heure=date_heure
#                 )

#         return "Planification réussie ✅"
#     else:
#         return "Aucune solution trouvée ❌"


# def generer_emploi_du_temps():
#     model = cp_model.CpModel()
#     matieres = list(Matiere.objects.all())
#     enseignants = list(Enseignant.objects.all())
#     groupes = list(Groupe.objects.all())
#     salles = list(Salle.objects.all())
#     affectations = list(Affectation.objects.all())
#     disponibilites = {dispo.enseignant.id: dispo.date_heure for dispo in DisponibiliteEnseignant.objects.all()}
#     jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
#     plages_horaires = list(range(1, 6))  # Plages horaires: 1 - 5
#     emploi = {}
    
#     # Création des variables de décision
#     for affectation in affectations:
#         for salle in salles:
#             for jour in range(len(jours)):
#                 for plage in plages_horaires:
#                     emploi[(affectation.id, salle.id, jour, plage)] = model.NewBoolVar(f"{affectation.matiere.nom}_{affectation.enseignant.nom}_{affectation.groupe.nom}_{salle.nom}_{jours[jour]}_{plage}")

#     # Ajout des contraintes (exemples simplifiés)
#     for affectation in affectations:
#         for salle in salles:
#             for jour in range(len(jours)):
#                 for plage in plages_horaires:
#                     if disponibilites.get(affectation.enseignant.id) and f"{jours[jour]} {plage}" not in disponibilites[affectation.enseignant.id]:
#                         model.Add(emploi[(affectation.id, salle.id, jour, plage)] == 0)

#     solver = cp_model.CpSolver()
#     status = solver.Solve(model)
    
#     if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
#         EmploiDuTemps.objects.all().delete()
        
#         for (affectation_id, salle_id, jour, plage), var in emploi.items():
#             if solver.Value(var) == 1:
#                 affectation = Affectation.objects.get(id=affectation_id)
#                 salle = Salle.objects.get(id=salle_id)
#                 date_heure = datetime.strptime(f"{jours[jour]} {plage}", "%A %H:%M")
#                 date_heure = make_aware(date_heure)
                
#                 EmploiDuTemps.objects.create(
#                     groupe=affectation.groupe,
#                     enseignant=affectation.enseignant,
#                     matiere=affectation.matiere,
#                     salle=salle,
#                     date_heure=date_heure
#                 )
        
#         return "Planification réussie ✅"
#     else:
#         return "Aucune solution trouvée ❌"

@csrf_exempt
def ajouter_affectation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)  # Debugging: Check the received data
        
        try:
            enseignant = get_object_or_404(Enseignant, id=data['enseignant_id'])
            matiere = get_object_or_404(Matiere, id=data['matiere_id'])
            groupe = get_object_or_404(Groupe, id=data['groupe_id'])
            
            affectation = Affectation.objects.create(
                enseignant=enseignant,
                matiere=matiere,
                groupe=groupe,
                type_cours=data['type_cours']
            )
            return JsonResponse({'message': 'Affectation ajoutée avec succès', 'id': affectation.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def supprimer_affectation(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Affectation.objects.get(id=data['id']).delete()
        return JsonResponse({'message': 'Affectation supprimée avec succès'})



@csrf_exempt
def ajouter_salle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        salle = Salle.objects.create(
            nom=data['nom'],
            capacite=int(data['capacite']),
            type_salle=data['type_salle']
        )
        return JsonResponse({'message': 'Salle ajoutée avec succès', 'id': salle.id})

@csrf_exempt
def modifier_salle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        salle = get_object_or_404(Salle, id=data['id'])
        salle.nom = data['nom']
        salle.capacite = int(data['capacite'])
        salle.type_salle = data['type_salle']
        salle.save()
        return JsonResponse({'message': 'Salle modifiée avec succès'})

@csrf_exempt
def supprimer_salle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        Salle.objects.get(id=data['id']).delete()
        return JsonResponse({'message': 'Salle supprimée avec succès'})

def afficher_salles(request):
    salles = Salle.objects.all()
    return render(request, "planning/salles.html", {"salles": salles})


def afficher_dashboard(request):
    """
    Vue pour afficher le tableau de bord du système.
    """
    context = {
        "total_matieres": Matiere.objects.count(),
        "total_enseignants": Enseignant.objects.count(),
        "total_groupes": Groupe.objects.count(),
        "total_salles": Salle.objects.count(),
        "dernier_emplois": EmploiDuTemps.objects.order_by("-date_heure")[:5],  # Derniers emplois du temps
    }

    return render(request, "planning/dashboard.html", context)

from ortools.sat.python import cp_model
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from django.apps import apps

def generer_emploi_du_temps():
    """
    Génère automatiquement l’emploi du temps en respectant les disponibilités des enseignants.
    """
    # Charger les modèles
    Matiere = apps.get_model('planning', 'Matiere')
    Enseignant = apps.get_model('planning', 'Enseignant')
    Groupe = apps.get_model('planning', 'Groupe')
    Affectation = apps.get_model('planning', 'Affectation')
    DisponibiliteEnseignant = apps.get_model('planning', 'DisponibiliteEnseignant')
    EmploiDuTemps = apps.get_model('planning', 'EmploiDuTemps')
    Salle = apps.get_model('planning', 'Salle')

    # Supprimer les emplois futurs
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
                    emploi[(affectation.id, j, h, salle.id)] = model.NewBoolVar(
                        f"{affectation.matiere.nom}_{affectation.groupe.nom}_{jour}_{heure}")

    # Contraintes : Respect des disponibilités des enseignants
    for affectation in affectations:
        if affectation.enseignant.id in disponibilites:
            dispo_date = disponibilites[affectation.enseignant.id]
            jour_index = dispo_date.weekday() % len(jours)
            heure_index = horaires.index(dispo_date.strftime("%H:%M"))
            for salle in salles:
                model.Add(emploi[(affectation.id, jour_index, heure_index, salle.id)] == 1)

    # Contraintes : Un enseignant ne peut pas être affecté à deux cours en même temps
    for enseignant in Enseignant.objects.all():
        for j, jour in enumerate(jours):
            for h, heure in enumerate(horaires):
                model.Add(sum(emploi[(a.id, j, h, salle.id)] for a in affectations if a.enseignant == enseignant for salle in salles) <= 1)

    # Contraintes : Une seule salle par créneau
    for j, jour in enumerate(jours):
        for h, heure in enumerate(horaires):
            for salle in salles:
                model.Add(sum(emploi[(a.id, j, h, salle.id)] for a in affectations) <= 1)

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

def afficher_emploi_du_temps(request):
    emplois = EmploiDuTemps.objects.all()
    groupes = Groupe.objects.all()
    enseignants = Enseignant.objects.all()

    print("📌 Emplois récupérés :", list(emplois))  # 🔍 Debugging dans la console

    return render(request, "planning/emploi_du_temps.html", {
        "emplois": emplois,
        "groupes": groupes,
        "enseignants": enseignants
    })

def planifier_emploi_du_temps(request):
    resultat = generer_emploi_du_temps()
    return JsonResponse({"message": resultat})