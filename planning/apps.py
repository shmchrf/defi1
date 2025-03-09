from django.apps import AppConfig

class PlanningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'planning'

    def ready(self):
        from django.db.utils import OperationalError
        from django.db import connection

        try:
            # Vérifier si la base de données est prête avant d'exécuter la planification
            if connection.ensure_connection():
                from .scheduler import generer_emploi_du_temps
                generer_emploi_du_temps()
        except OperationalError:
            print("⚠️ La base de données n'est pas encore prête, la génération de l'emploi sera exécutée plus tard.")
