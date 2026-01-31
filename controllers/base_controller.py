import json
import logging
import os

# Chemin du dossier data par rapport au projet (depuis controllers/)
logger = logging.getLogger(__name__)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "data")


class BaseController:
    def __init__(self, filename):
        self.filename = os.path.join(_DATA_DIR, filename)
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, OSError) as e:
            # Fichier JSON invalide, vide ou illisible : repartir sur une liste vide
            logger.warning("Impossible de charger %s : %s. Données vides utilisées.", self.filename, e)
            return []

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def create(self, obj_dict):
        self.data.append(obj_dict)
        self.save()

    def read_all(self):
        # Toujours recharger le fichier pour que toutes les vues
        # voient les données les plus récentes (créations/modifications
        # faites depuis un autre onglet, par exemple les étudiants
        # utilisés dans l'onglet Notes).
        self.data = self.load()
        return self.data

    def update(self, index, new_data):
        self.data[index] = new_data
        self.save()

    def delete(self, index):
        del self.data[index]
        self.save()
