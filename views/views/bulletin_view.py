import tkinter as tk
from tkinter import ttk

from controllers.etudiant_controller import EtudiantController
from controllers.departement_controller import DepartementController
from controllers.note_controller import NoteController
from controllers.matiere_controller import MatiereController
from services.moyenne_service import MoyenneService
from services.moyenne_generale_service import MoyenneGeneraleService
from services.rang_service import RangService


class BulletinView(tk.Frame):
	"""Vue de bulletin de notes.

	- Liste des étudiants à gauche (avec filtre par niveau).
	- À droite :
		* Informations de l'étudiant (matricule, nom, prénom, département, niveau)
		* Tableau des matières : code, nom, coefficient, moyenne
		* En bas : somme des coefficients, moyenne générale, rang.
	"""

	NIVEAUX = ["", "L1", "L2", "L3", "M1", "M2", "D"]

	def __init__(self, master):
		super().__init__(master)
		self.master = master

		self.etudiant_controller = EtudiantController()
		self.departement_controller = DepartementController()
		self.note_controller = NoteController()
		self.matiere_controller = MatiereController()
		self.moyenne_service = MoyenneService()
		self.moyenne_generale_service = MoyenneGeneraleService()
		self.rang_service = RangService()

		self.all_students = []
		self.filtered_students = []

		self.pack(fill=tk.BOTH, expand=True)

		# --- Bandeau haut (filtres niveau + département) ---
		top_bar = tk.Frame(self)
		top_bar.pack(fill=tk.X, padx=10, pady=8)

		tk.Label(top_bar, text="Niveau :").pack(side=tk.LEFT)
		self.level_var = tk.StringVar(value="")
		level_cb = ttk.Combobox(top_bar, textvariable=self.level_var, values=self.NIVEAUX, width=8, state="readonly")
		level_cb.pack(side=tk.LEFT, padx=(4, 8))
		level_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_students_list())

		tk.Label(top_bar, text="Département :").pack(side=tk.LEFT)
		self.dept_var = tk.StringVar(value="Tous")
		self.dept_choices = ["Tous"]
		self.dept_display_to_index = {}
		self.dept_cb = ttk.Combobox(top_bar, textvariable=self.dept_var, values=self.dept_choices, width=18, state="readonly")
		self.dept_cb.pack(side=tk.LEFT, padx=(4, 0))
		self.dept_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_students_list())

		# --- Zone centrale ---
		center = tk.Frame(self)
		center.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

		center.columnconfigure(0, weight=1)
		center.columnconfigure(1, weight=4)
		center.rowconfigure(0, weight=1)

		# Liste des étudiants (gauche)
		left_frame = tk.Frame(center, bd=1, relief=tk.SOLID)
		left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

		tk.Label(left_frame, text="Étudiants", anchor="w").pack(fill=tk.X, padx=6, pady=4)

		self.student_listbox = tk.Listbox(left_frame, exportselection=False)
		self.student_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))
		self.student_listbox.bind("<<ListboxSelect>>", lambda e: self.refresh_bulletin())

		# Zone droite : infos + tableau + résumé
		right_frame = tk.Frame(center, bd=1, relief=tk.SOLID)
		right_frame.grid(row=0, column=1, sticky="nsew")

		# Infos étudiant
		info_frame = tk.Frame(right_frame)
		info_frame.pack(fill=tk.X, padx=6, pady=6)

		self.label_matricule = tk.Label(info_frame, text="Matricule :")
		self.label_matricule.grid(row=0, column=0, sticky="w")
		self.value_matricule = tk.Label(info_frame, text="-")
		self.value_matricule.grid(row=0, column=1, sticky="w", padx=(4, 12))

		self.label_nom = tk.Label(info_frame, text="Nom :")
		self.label_nom.grid(row=0, column=2, sticky="w")
		self.value_nom = tk.Label(info_frame, text="-")
		self.value_nom.grid(row=0, column=3, sticky="w", padx=(4, 12))

		self.label_prenom = tk.Label(info_frame, text="Prénom :")
		self.label_prenom.grid(row=1, column=0, sticky="w")
		self.value_prenom = tk.Label(info_frame, text="-")
		self.value_prenom.grid(row=1, column=1, sticky="w", padx=(4, 12))

		self.label_niveau = tk.Label(info_frame, text="Niveau :")
		self.label_niveau.grid(row=1, column=2, sticky="w")
		self.value_niveau = tk.Label(info_frame, text="-")
		self.value_niveau.grid(row=1, column=3, sticky="w", padx=(4, 12))

		self.label_dept = tk.Label(info_frame, text="Département :")
		self.label_dept.grid(row=2, column=0, sticky="w")
		self.value_dept = tk.Label(info_frame, text="-")
		self.value_dept.grid(row=2, column=1, sticky="w", padx=(4, 12))

		# Tableau des matières (moyenne avant coefficient)
		self.fields = ["code_matiere", "nom_matiere", "moyenne", "coefficient"]
		# Style pour avoir les entêtes en gras (sans bordures spéciales)
		style = ttk.Style()
		style.configure("Bulletin.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))
		self.table = ttk.Treeview(right_frame, columns=self.fields, show="headings", style="Bulletin.Treeview")
		for f in self.fields:
			if f == "code_matiere":
				head = "Code"
			elif f == "nom_matiere":
				head = "Matière"
			elif f == "moyenne":
				head = "Moyenne"
			else:
				head = "Coef"
			self.table.heading(f, text=head)
			self.table.column(f, width=120, anchor="center")
		self.table.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

		# Résumé en bas
		summary = tk.Frame(right_frame)
		summary.pack(fill=tk.X, padx=6, pady=6)

		self.label_somme_coef = tk.Label(summary, text="Somme des coefficients : 0")
		self.label_somme_coef.pack(side=tk.LEFT, padx=(0, 16))

		self.label_moy_gen = tk.Label(summary, text="Moyenne générale : 0.00")
		self.label_moy_gen.pack(side=tk.LEFT, padx=(0, 16))

		self.label_rang = tk.Label(summary, text="Rang : -")
		self.label_rang.pack(side=tk.LEFT)

		# Charger données initiales
		self._load_departements()
		self.refresh_students_list()
		self.refresh_bulletin()

	# --- Liste des étudiants ---
	def refresh_students_list(self):
		self.student_listbox.delete(0, tk.END)

		try:
			self.all_students = self.etudiant_controller.read_all()
		except Exception:
			self.all_students = []

		selected_level = self.level_var.get() or ""
		selected_dept_label = self.dept_var.get() if hasattr(self, "dept_var") else "Tous"
		selected_dept_index = self.dept_display_to_index.get(selected_dept_label) if hasattr(self, "dept_display_to_index") else None

		self.filtered_students = []
		for e in self.all_students:
			if not isinstance(e, dict):
				continue
			if selected_level and e.get("niveau") != selected_level:
				continue
			if selected_dept_index is not None and e.get("departement_index") != selected_dept_index:
				continue
			self.filtered_students.append(e)
			mat = e.get("matricule", "")
			nom = e.get("nom", "")
			prenom = e.get("prenom", "")
			display = f"{mat} - {nom} {prenom}"
			self.student_listbox.insert(tk.END, display)

		if self.filtered_students:
			self.student_listbox.selection_set(0)

	# --- Utilitaire : étudiant sélectionné ---
	def get_selected_student(self):
		sel = self.student_listbox.curselection()
		if not sel:
			return None
		idx = sel[0]
		if idx < 0 or idx >= len(self.filtered_students):
			return None
		return self.filtered_students[idx]

	# --- Rafraîchir bulletin pour l'étudiant sélectionné ---
	def refresh_bulletin(self):
		for r in self.table.get_children():
			self.table.delete(r)

		student = self.get_selected_student()
		if not student:
			self._clear_student_info()
			return

		# Infos de base
		matricule = student.get("matricule", "")
		nom = student.get("nom", "")
		prenom = student.get("prenom", "")
		niveau = student.get("niveau", "")
		dept_index = student.get("departement_index")

		self.value_matricule.config(text=matricule)
		self.value_nom.config(text=nom)
		self.value_prenom.config(text=prenom)
		self.value_niveau.config(text=niveau)
		self.value_dept.config(text=self._get_departement_nom(dept_index))

		# Récupérer les matières où l'étudiant a des notes pour ce niveau
		codes_matieres = self._get_matieres_pour_etudiant_et_niveau(matricule, niveau)

		# Indexer les matières pour connaître nom + coefficient
		matieres_index = self._indexer_matieres()

		somme_coef = 0.0
		somme_moy_x_coef = 0.0

		for code in sorted(codes_matieres):
			matiere_data = matieres_index.get(code)
			if not matiere_data:
				continue

			nom_matiere = matiere_data.get("nom_matiere", "")
			coef = float(matiere_data.get("coefficient", 0.0) or 0.0)
			moy = self.moyenne_service.calculer_moyenne_matiere_etudiant(matricule, code, niveau)

			# On affiche la moyenne avant le coefficient
			self.table.insert("", "end", values=[code, nom_matiere, f"{moy:.2f}", f"{coef:.2f}"])

			somme_coef += coef
			somme_moy_x_coef += moy * coef

		# Moyenne générale (via service pour cohérence)
		moy_gen = self.moyenne_generale_service.calculer_moyenne_generale(matricule, niveau)

		self.label_somme_coef.config(text=f"Somme des coefficients : {somme_coef:.2f}")
		self.label_moy_gen.config(text=f"Moyenne générale : {moy_gen:.2f}")

		# Rang
		rang, effectif = self.rang_service.calculer_rang(matricule, dept_index, niveau)
		if rang is None or effectif == 0:
			self.label_rang.config(text="Rang : -")
		else:
			self.label_rang.config(text=f"Rang : {rang}/{effectif}")

	def _clear_student_info(self):
		self.value_matricule.config(text="-")
		self.value_nom.config(text="-")
		self.value_prenom.config(text="-")
		self.value_niveau.config(text="-")
		self.value_dept.config(text="-")
		self.label_somme_coef.config(text="Somme des coefficients : 0")
		self.label_moy_gen.config(text="Moyenne générale : 0.00")
		self.label_rang.config(text="Rang : -")

	def _get_departement_nom(self, index):
		try:
			deps = self.departement_controller.read_all()
		except Exception:
			deps = []
		if isinstance(index, int) and 0 <= index < len(deps):
			d = deps[index]
			if isinstance(d, dict):
				return d.get("nom_departement", "-")
		return "-"

	def _load_departements(self):
		"""Charge les départements pour le filtre haut."""
		try:
			deps = self.departement_controller.read_all()
		except Exception:
			deps = []

		self.dept_choices = ["Tous"]
		self.dept_display_to_index = {}
		for idx, d in enumerate(deps):
			if isinstance(d, dict):
				nom = d.get("nom_departement", "")
			else:
				nom = str(d)
			label = nom or f"Département {idx+1}"
			self.dept_choices.append(label)
			self.dept_display_to_index[label] = idx

		# Mettre à jour les valeurs de la combobox
		if hasattr(self, "dept_cb"):
			self.dept_cb["values"] = self.dept_choices

		# S'assurer que la valeur sélectionnée est valide
		current = self.dept_var.get()
		if current not in self.dept_choices:
			self.dept_var.set("Tous")

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
