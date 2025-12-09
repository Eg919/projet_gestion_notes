from controllers.etudiant_controller import EtudiantController
from controllers.departement_controller import DepartementController
from controllers.note_controller import NoteController
from controllers.matiere_controller import MatiereController
from services.moyenne_service import MoyenneService
from services.moyenne_generale_service import MoyenneGeneraleService
from services.rang_service import RangService


class BulletinController:
	"""Contrôleur dédié à la logique métier du bulletin.

	- Récupération des étudiants
	- Calcul des lignes de matières (moyenne par matière, coefficient)
	- Calcul de la moyenne générale et du rang
	"""

	def __init__(self):
		self.etudiant_controller = EtudiantController()
		self.departement_controller = DepartementController()
		self.note_controller = NoteController()
		self.matiere_controller = MatiereController()
		self.moyenne_service = MoyenneService()
		self.moyenne_generale_service = MoyenneGeneraleService()
		self.rang_service = RangService()

	def get_all_students(self):
		"""Renvoie la liste complète des étudiants (ou [] en cas d'erreur)."""
		try:
			return self.etudiant_controller.read_all()
		except Exception:
			return []

	def get_departement_nom(self, index):
		"""Renvoie le nom du département à partir de son index."""
		try:
			deps = self.departement_controller.read_all()
		except Exception:
			deps = []
		if isinstance(index, int) and 0 <= index < len(deps):
			d = deps[index]
			if isinstance(d, dict):
				return d.get("nom_departement", "-")
		return "-"

	def get_bulletin_data(self, matricule: str, niveau: str, departement_index):
		"""Construit toutes les données du bulletin pour un étudiant donné.

		Retourne un dict :
		{
			"matieres": [
				{"code_matiere": str, "nom_matiere": str, "moyenne": float, "coefficient": float},
			],
			"somme_coef": float,
			"moyenne_generale": float,
			"rang": Optional[int],
			"effectif": int,
		}
		"""
		codes_matieres = self._get_matieres_pour_etudiant_et_niveau(matricule, niveau)
		matieres_index = self._indexer_matieres()

		lignes = []
		somme_coef = 0.0
		somme_moy_x_coef = 0.0

		for code in sorted(codes_matieres):
			matiere_data = matieres_index.get(code)
			if not matiere_data:
				continue

			nom_matiere = matiere_data.get("nom_matiere", "")
			coef = float(matiere_data.get("coefficient", 0.0) or 0.0)
			moy = self.moyenne_service.calculer_moyenne_matiere_etudiant(matricule, code, niveau)

			lignes.append(
				{
					"code_matiere": code,
					"nom_matiere": nom_matiere,
					"moyenne": moy,
					"coefficient": coef,
				}
			)

			somme_coef += coef
			somme_moy_x_coef += moy * coef

		# Moyenne générale (via service dédié)
		moy_gen = self.moyenne_generale_service.calculer_moyenne_generale(matricule, niveau)

		# Rang dans le département / niveau
		rang, effectif = self.rang_service.calculer_rang(matricule, departement_index, niveau)

		return {
			"matieres": lignes,
			"somme_coef": somme_coef,
			"moyenne_generale": moy_gen,
			"rang": rang,
			"effectif": effectif or 0,
		}

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
		"""Construit un index {code_matiere: matiere_dict}."""
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
