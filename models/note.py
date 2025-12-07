from datetime import date

class Note:
    def __init__(self, idNote, valeur, typeEvaluation, niveau, dateSaisie=None):
        self.idNote = idNote
        self.valeur = valeur
        self.typeEvaluation = typeEvaluation
        self.niveau = niveau
        self.dateSaisie = dateSaisie or date.today()

        # relations renseignées par les méthodes des autres classes
        self.etudiant = None
        self.matiere = None
