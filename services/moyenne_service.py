from controllers.note_controller import NoteController
from controllers.matiere_controller import MatiereController


class MoyenneService:
	"""Service de calcul des moyennes par matière / étudiant / niveau.

	Méthode principale :
	- calculer_moyenne_matiere_etudiant(matricule, code_matiere, niveau)
	"""

	def __init__(self):
		self.note_controller = NoteController()
		self.matiere_controller = MatiereController()

	def calculer_moyenne_matiere_etudiant(self, matricule: str, code_matiere: str, niveau: str) -> float:
		"""Calcule la moyenne d'une matière pour un étudiant et un niveau donné.

		Formule :
		  somme( note * coefficient_type ) / somme( coefficient_type )
		où coefficient_type dépend de typeEvaluation :
		  - "CC" ou "cot" -> coefficient_cc (anciennement coefficient_cot)
		  - "TP"           -> coefficient_tp
		  - "EX"           -> coefficient_ex

		Retourne 0.0 si aucune note correspondante ou si la somme des
		coefficients est nulle.
		"""

		# Récupérer la matière pour connaître ses coefficients
		try:
			matieres = self.matiere_controller.read_all()
		except Exception:
			matieres = []

		matiere_data = None
		for m in matieres:
			if isinstance(m, dict) and m.get("code_matiere") == code_matiere:
				matiere_data = m
				break

		if not matiere_data:
			return 0.0

		# Compatibilité : accepter encore l'ancien champ "coefficient_cot"
		coef_cc = float(
			matiere_data.get("coefficient_cc",
						 matiere_data.get("coefficient_cot", 0.0))
			or 0.0
		)
		coef_tp = float(matiere_data.get("coefficient_tp", 0.0) or 0.0)
		coef_ex = float(matiere_data.get("coefficient_ex", 0.0) or 0.0)

		# Récupérer les notes correspondantes
		try:
			notes = self.note_controller.read_all()
		except Exception:
			notes = []

		somme_ponderee = 0.0
		somme_coef = 0.0

		for n in notes:
			if not isinstance(n, dict):
				continue
			if n.get("matricule") != matricule:
				continue
			if n.get("code_matiere") != code_matiere:
				continue
			if n.get("niveau") != niveau:
				continue

			valeur = float(n.get("valeur", 0.0) or 0.0)
			type_eval = n.get("typeEvaluation", "").lower()

			# Accepter les anciens codes ("cot") et les nouveaux ("CC")
			if type_eval in ("cot", "cc"):
				coef = coef_cc
			elif type_eval == "tp":
				coef = coef_tp
			elif type_eval == "ex":
				coef = coef_ex
			else:
				# type inconnu, on ignore
				continue

			if coef <= 0:
				continue

			somme_ponderee += valeur * coef
			somme_coef += coef

		if somme_coef == 0:
			return 0.0

		return somme_ponderee / somme_coef
