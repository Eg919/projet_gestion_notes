class Departement:
    def __init__(self, nom_departement, sigle_departement):
        self.nom_departement = nom_departement
        self.sigle_departement = sigle_departement
        self.etudiants = []
    def ajouter_etudiant(self, etudiant):
        self.etudiants.append(etudiant)
        etudiant.departement = self

    def to_dict(self):
        return {
            "nom_departement": self.nom_departement,
            "sigle_departement": self.sigle_departement,
            "etudiants": [e.to_dict() for e in self.etudiants] if self.etudiants else [],
            "administrateurs": [a.to_dict() for a in self.administrateurs] if self.administrateurs else []
        }
