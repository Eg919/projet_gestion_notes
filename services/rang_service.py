from typing import Tuple, Optional

from controllers.etudiant_controller import EtudiantController
from services.moyenne_generale_service import MoyenneGeneraleService


class RangService:
	"""Service pour déterminer le rang d'un étudiant.

	Calcule le rang d'un étudiant dans un département donné et pour
	un niveau donné, en se basant sur la moyenne générale calculée
	par `MoyenneGeneraleService`.
	"""

	def __init__(self):
		self.etudiant_controller = EtudiantController()
		self.moyenne_generale_service = MoyenneGeneraleService()

	def calculer_rang(self, matricule: str, departement_index: int, niveau: str) -> Tuple[Optional[int], int]:
		"""Retourne (rang, effectif) pour un étudiant.

		- `rang` est la position (1 = meilleur) de l'étudiant dans son
		  département et niveau.
		- `effectif` est le nombre total d'étudiants pris en compte.
		- Si l'étudiant n'est pas trouvé dans le groupe, `rang` vaut None.
		"""

		try:
			etudiants = self.etudiant_controller.read_all()
		except Exception:
			etudiants = []

		# Filtrer les étudiants du même département et même niveau
		candidats = []  # liste de matricules
		for e in etudiants:
			if not isinstance(e, dict):
				continue
			if e.get("departement_index") != departement_index:
				continue
			if e.get("niveau") != niveau:
				continue
			mat = e.get("matricule")
			if mat:
				candidats.append(mat)

		if not candidats:
			return None, 0

		# Calculer la moyenne générale de chaque candidat
		notes_par_etudiant = []  # (matricule, moyenne_generale)
		for mat in candidats:
			moy = self.moyenne_generale_service.calculer_moyenne_generale(mat, niveau)
			notes_par_etudiant.append((mat, moy))

		# Trier par moyenne décroissante
		notes_par_etudiant.sort(key=lambda x: x[1], reverse=True)

		# Trouver le rang de l'étudiant
		rang = None
		for idx, (mat, moy) in enumerate(notes_par_etudiant, start=1):
			if mat == matricule:
				rang = idx
				break

		return rang, len(notes_par_etudiant)
