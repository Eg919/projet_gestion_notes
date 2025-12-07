import json
import os

class BaseController:
    def __init__(self, filename):
        self.filename = os.path.join("data", filename)
        self.data = self.load()

    def load(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, "r") as f:
            try:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
            except Exception:
                # Fichier JSON invalide ou vide : repartir sur une liste vide
                return []

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def create(self, obj_dict):
        self.data.append(obj_dict)
        self.save()

    def read_all(self):
        return self.data

    def update(self, index, new_data):
        self.data[index] = new_data
        self.save()

    def delete(self, index):
        del self.data[index]
        self.save()
