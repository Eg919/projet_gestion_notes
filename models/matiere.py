class Matiere:
    def __init__(self, code_matiere, nom_matiere,
				 coefficient=0.0, coefficient_cc=0.0,
                 coefficient_tp=0.0, coefficient_ex=0.0):
        self.code_matiere = code_matiere
        self.nom_matiere = nom_matiere
        self.coefficient = float(coefficient)
		self.coefficient_cc = float(coefficient_cc)
        self.coefficient_tp = float(coefficient_tp)
        self.coefficient_ex = float(coefficient_ex)
        self.notes = []  # Liste des notes associées à la matière

    def ajouter_note(self, note):
        """Ajoute une note à cette matière"""
        self.notes.append(note)
        note.matiere = self

    def to_dict(self):
        """Convertit l'objet Matiere en dictionnaire pour JSON"""
        return {
            "code_matiere": self.code_matiere,
            "nom_matiere": self.nom_matiere,
            "coefficient": self.coefficient,
			"coefficient_cc": self.coefficient_cc,
            "coefficient_tp": self.coefficient_tp,
            "coefficient_ex": self.coefficient_ex,
            # On ne sauvegarde pas les notes pour l'instant
        }

    @staticmethod
    def from_dict(data: dict):
        """Crée un objet Matiere à partir d'un dictionnaire"""
		# Compatibilité : accepter l'ancien nom de champ "coefficient_cot"
		coef_cc = data.get("coefficient_cc")
		if coef_cc is None:
			coef_cc = data.get("coefficient_cot", 0.0)

        return Matiere(
            code_matiere=data.get("code_matiere", ""),
            nom_matiere=data.get("nom_matiere", ""),
            coefficient=data.get("coefficient", 0.0),
			coefficient_cc=coef_cc,
            coefficient_tp=data.get("coefficient_tp", 0.0),
            coefficient_ex=data.get("coefficient_ex", 0.0)
        )
