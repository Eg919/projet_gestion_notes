from typing import Optional

from controllers.matiere_controller import MatiereController
from controllers.note_controller import NoteController
from services.moyenne_service import MoyenneService


class MoyenneGeneraleService:
	"""Service pour calculer la moyenne générale d'un étudiant à un niveau donné.

	La moyenne générale est calculée à partir des moyennes par matière
	(`MoyenneService.calculer_moyenne_matiere_etudiant`) pondérées par le
	coefficient global de chaque matière.

	Formule :
	  somme( moyenne_matiere * coefficient_matiere ) / somme( coefficient_matiere )
	"""

	def __init__(self):
		self.note_controller = NoteController()
		self.matiere_controller = MatiereController()
		self.moyenne_service = MoyenneService()

	def calculer_moyenne_generale(self, matricule: str, niveau: str) -> float:
		"""Calcule la moyenne générale d'un étudiant pour un niveau donné.

		- Récupère toutes les notes de l'étudiant pour ce niveau.
		- Identifie les différentes matières concernées.
		- Pour chaque matière, calcule la moyenne de la matière via
		  `MoyenneService.calculer_moyenne_matiere_etudiant`.
		- Pèse chaque moyenne par le coefficient global de la matière
		  (`coefficient`).

		Retourne 0.0 si aucune matière/coefficient valide.
		"""

		codes_matieres = self._get_matieres_pour_etudiant_et_niveau(matricule, niveau)
		if not codes_matieres:
			return 0.0

		# Indexer les matières par code pour récupérer rapidement le coefficient
		matieres_index = self._indexer_matieres()

		somme_ponderee = 0.0
		somme_coef = 0.0

		for code_matiere in codes_matieres:
			matiere_data = matieres_index.get(code_matiere)
			if not matiere_data:
				continue

			coef_global = float(matiere_data.get("coefficient", 0.0) or 0.0)
			if coef_global <= 0:
				continue

			moy_matiere = self.moyenne_service.calculer_moyenne_matiere_etudiant(
				matricule=matricule,
				code_matiere=code_matiere,
				niveau=niveau,
			)

			# Si aucune note/moyenne, on ignore cette matière
			if moy_matiere <= 0 and not self._a_notes_pour_matiere(matricule, code_matiere, niveau):
				continue

			somme_ponderee += moy_matiere * coef_global
			somme_coef += coef_global

		if somme_coef == 0:
			return 0.0

		return somme_ponderee / somme_coef

	def _get_matieres_pour_etudiant_et_niveau(self, matricule: str, niveau: str) -> set:
		"""Renvoie l'ensemble des codes de matières pour un étudiant/niveau."""
		try:
			notes = self.note_controller.read_all()
		except Exception:
			notes = []

		codes = set()
		for n in notes:
			if not isinstance(n, dict):
				continue
			if n.get("matricule") != matricule:
				continue
			if n.get("niveau") != niveau:
				continue
			code = n.get("code_matiere")
			if code:
				codes.add(code)
		return codes

	def _indexer_matieres(self) -> dict:
		"""Construit un dictionnaire {code_matiere: matiere_dict}."""
		try:
			matieres = self.matiere_controller.read_all()
		except Exception:
			matieres = []

		index = {}
		for m in matieres:
			if not isinstance(m, dict):
				continue
			code = m.get("code_matiere")
			if code:
				index[code] = m
		return index

	def _a_notes_pour_matiere(self, matricule: str, code_matiere: str, niveau: str) -> bool:
		"""Vérifie s'il existe au moins une note pour une matière donnée."""
		try:
			notes = self.note_controller.read_all()
		except Exception:
			notes = []

		for n in notes:
			if not isinstance(n, dict):
				continue
			if n.get("matricule") != matricule:
				continue
			if n.get("code_matiere") != code_matiere:
				continue
			if n.get("niveau") != niveau:
				continue
			return True
		return False
