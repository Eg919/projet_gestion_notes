class Etudiant:
    def __init__(self, matricule, nom, prenom, niveau):
        self.matricule = matricule
        self.nom = nom
        self.prenom = prenom
        self.niveau = niveau
        self.departement = None  # 1..1 relation
        self.notes = []  # 0..* relation avec Note

    def ajouter_note(self, note):
        self.notes.append(note)
        note.etudiant = self

    def calcul_moyenne(self):
        if not self.notes:
            return 0
        total = sum([n.valeur for n in self.notes])
        return total / len(self.notes)
