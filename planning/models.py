import uuid
from django.db import models

# ===  GESTION DES MATIÈRES ===
class Matiere(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, unique=True)
    nom = models.CharField(max_length=100)
    credits = models.IntegerField()
    semestre = models.IntegerField(choices=[(i, f"Semestre {i}") for i in range(1, 7)])
    filiere = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

# ===  GESTION DES ENSEIGNANTS ===
class Enseignant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    disponibilites = models.JSONField(default=dict, blank=True)  # {"Lundi": [1,2], "Mardi": [3,4]}

    def __str__(self):
        return self.nom



class Groupe(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=50, unique=True)
    semestre = models.IntegerField(choices=[(i, f"Semestre {i}") for i in range(1, 7)])
    parent_groupe = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name="sous_groupes"
    )

    def __str__(self):
        if self.parent_groupe:
            return f"{self.nom} (Sous-groupe de {self.parent_groupe.nom})"
        return self.nom



# ===  AFFECTATION DES ENSEIGNANTS AUX GROUPES ===
class Affectation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    type_cours = models.CharField(max_length=10, choices=[("CM", "CM"), ("TD", "TD"), ("TP", "TP")])


# ===  DISPONIBILITÉS DES ENSEIGNANTS (Avec date et heure) ===
class DisponibiliteEnseignant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    date_heure = models.DateTimeField()  # Date et Heure de la disponibilité

    def __str__(self):
        return f"{self.enseignant.nom} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"

# ===  GESTION DES SALLES ===
class Salle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=50, unique=True)
    capacite = models.IntegerField()
    type_salle = models.CharField(max_length=50, choices=[("CM", "CM"), ("TD", "TD"), ("TP", "TP")])

    def __str__(self):
        return self.nom

# ===  CALENDRIER DES SEMAINES ===
class Calendrier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    semaine = models.IntegerField()  # Numéro de la semaine
    jour = models.DateField()
    exception = models.BooleanField(default=False)  # Si la journée a été modifiée par l'admin

# ===  CHARGES HEBDOMADAIRES À PLANIFIER ===
class ChargeHoraire(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    cm = models.IntegerField(default=0)  # Nombre de séances de CM
    td = models.IntegerField(default=0)  # Nombre de séances de TD
    tp = models.IntegerField(default=0)  # Nombre de séances de TP

# ===  EMPLOI DU TEMPS ===
# models.py

class EmploiDuTemps(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Correction ici
    date_heure = models.DateTimeField()

    def __str__(self):
        return f"{self.groupe.nom} - {self.matiere.nom} - {self.enseignant.nom} - {self.date_heure}"


class Affectation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
    type_cours = models.CharField(max_length=10, choices=[("CM", "CM"), ("TD", "TD"), ("TP", "TP")])

    def __str__(self):
        return f"{self.enseignant.nom} -> {self.matiere.nom} ({self.type_cours}) - {self.groupe.nom}"
