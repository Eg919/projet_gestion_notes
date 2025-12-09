from models.etudiant import Etudiant
from models.matiere import  Matiere
from models.note import Note

class SystemeNotes:
    def __init__(self):
        self.etudiants: list[Etudiant] = []
        self.matieres: list[Matiere] = []
        self.notes: list[Note] = []

    def ajouter_etudiant(self,etudiant):
        if any(e.matricule == etudiant.matricule for e in self.etudiants):
            print("Étudiant déjà existant !")
        return self.etudiants.append(etudiant)

    def ajouter_matiere(self,matiere:Matiere):
        if any(m.code == matiere.code for m in self.matieres):
            print("Matière déjà existante !")
        return self.matieres.append(matiere)

    def ajouter_note(self,note:Note)-> bool:
        if not note.est_valide():
            print(f"Note invalide : {note.valeur}/20")

            return False
            # Vérifier qu'on n'a pas déjà une note du même type pour cet étudiant/matière
        for n in self.notes:
            if (n.etudiant.matricule == note.etudiant.matricule and
                    n.matiere.code == note.matiere.code and
                    n.type_eval == note.type_eval):
                print("Une note de ce type existe déjà pour cet étudiant dans cette matière")
                return False
        self.notes.append(note)
        return True

    def calculer_moyenne(self,etudiant:Etudiant,matiere:Matiere) -> float:
        notes_etudiant_matiere = [
            n for n in self.notes
            if n.etudiant.matricule == etudiant.matricule and n.matiere.code == matiere.code
        ]
        if not notes_etudiant_matiere:
            return - 1

        total = 0
        total_coeff = 0
        for note in notes_etudiant_matiere:
            coeff = matiere.get_coefficient(note.type_eval)
            total += note.valeur * coeff
            total_coeff += coeff
        return round(total/total_coeff, 2)


    def calculer_moyenne_generale(self, etudiant:Etudiant) -> float:
        moyennes_matieres = []
        for matiere in self.matieres:
            moyenne = self.calculer_moyenne(etudiant,matiere)
            if moyenne != -1:
                coeff_total = matiere.coef_cc + matiere.coef_tp + matiere.coef_examen
                moyennes_matieres.append(moyenne,coeff_total)

            if not moyennes_matieres:
                return -1
        total = sum(moyenne * coeff for moyenne, coeff in moyennes_matieres)
        total_coeff = sum(coeff for _, coeff in moyennes_matieres)
        return round(total/total_coeff, 2)

    def rechercher_par_nom(self,nom:str)-> list[Etudiant]:
        nom = nom.lower()
        return [e for e in self.etudiants if nom in e.nom.lower() or nom in e.prenom.lower()]


    def rechercher_par_matricule(self,matricule:str):
        for e in self.etudiants:
            if e.matricule == matricule:
                return e
        return None

    def rechercher_par_niveau(self, niveau:str):
        return  [e for e in self.etudiants if e.niveau.upper() == niveau.upper()]