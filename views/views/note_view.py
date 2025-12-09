import tkinter as tk
from tkinter import ttk, messagebox

from controllers.etudiant_controller import EtudiantController
from controllers.matiere_controller import MatiereController
from controllers.note_controller import NoteController
from controllers.departement_controller import DepartementController


class NoteView(tk.Frame):
	"""Onglet de gestion des notes.

	- Bandeau haut : boutons Ajouter / Modifier / Supprimer
	  + filtre par niveau (L1, L2, L3, M1, M2, D).
	- Zone centrale :
		* colonne gauche (20%) : liste des étudiants (filtrés par niveau)
		* colonne droite (80%) : notes de l'étudiant sélectionné
		  (matière, type d'évaluation, valeur, niveau).
	"""

	NIVEAUX = ["", "L1", "L2", "L3", "M1", "M2", "D"]
	# Types d'évaluation affichés à l'écran : CC, TP, EX
	TYPE_EVAL = ["CC", "TP", "EX"]  # correspondent aux coefficients coefficient_cc / coefficient_tp / coefficient_ex de Matiere

	def __init__(self, master):
		super().__init__(master)
		self.master = master

		self.etudiant_controller = EtudiantController()
		self.matiere_controller = MatiereController()
		self.note_controller = NoteController()
		self.departement_controller = DepartementController()

		self.all_students = []
		self.filtered_students = []
		self._current_notes_filtered = []

		self.matiere_choices = []
		self.matiere_display_to_data = {}

		self.pack(fill=tk.BOTH, expand=True)

		# --- Bandeau de commandes haut ---
		top_bar = tk.Frame(self)
		top_bar.pack(fill=tk.X, padx=10, pady=8)

		self.add_btn = tk.Button(top_bar, text="Ajouter", command=self.open_create_form)
		self.add_btn.pack(side=tk.LEFT, padx=(0, 6))

		self.edit_btn = tk.Button(top_bar, text="Modifier", command=self.open_edit_form)
		self.edit_btn.pack(side=tk.LEFT, padx=(0, 6))

		self.del_btn = tk.Button(top_bar, text="Supprimer", command=self.delete_note)
		self.del_btn.pack(side=tk.LEFT, padx=(0, 12))

		# Filtres niveau + département pour la liste d'étudiants
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

		# --- Zone centrale avec 2 colonnes ---
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
		self.student_listbox.bind("<<ListboxSelect>>", lambda e: self.on_student_select())

		# Table des notes (droite)
		right_frame = tk.Frame(center, bd=1, relief=tk.SOLID)
		right_frame.grid(row=0, column=1, sticky="nsew")

		tk.Label(right_frame, text="Notes de l'étudiant", anchor="w").pack(fill=tk.X, padx=6, pady=4)

		self.fields = ["nom_matiere", "typeEvaluation", "valeur", "niveau"]
		# Style pour avoir les entêtes en gras (sans bordures spéciales)
		style = ttk.Style()
		style.configure("Note.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))
		self.table = ttk.Treeview(right_frame, columns=self.fields, show="headings", style="Note.Treeview")
		for f in self.fields:
			if f == "nom_matiere":
				head = "Matière"
			elif f == "typeEvaluation":
				head = "Type"
			elif f == "valeur":
				head = "Note"
			else:
				head = "Niveau"
			self.table.heading(f, text=head)
			self.table.column(f, width=120, anchor="center")
		self.table.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

		# Charger les données
		self.load_matieres()
		self.load_departements()
		self.refresh_students_list()
		self.refresh_notes()

	# --- Chargement des matières pour le formulaire ---
	def load_matieres(self):
		try:
			matieres = self.matiere_controller.read_all()
		except Exception:
			matieres = []

		self.matiere_choices = []
		self.matiere_display_to_data = {}
		for m in matieres:
			if isinstance(m, dict):
				code = m.get("code_matiere", "")
				nom = m.get("nom_matiere", "")
			else:
				code = str(m)
				nom = ""
			label = f"{code} - {nom}" if nom else code
			self.matiere_choices.append(label)
			self.matiere_display_to_data[label] = {"code_matiere": code, "nom_matiere": nom}

	def load_departements(self):
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

	# --- Chargement de la liste d'étudiants (gauche) ---
	def refresh_students_list(self):
		self.student_listbox.delete(0, tk.END)

		try:
			self.all_students = self.etudiant_controller.read_all()
		except Exception:
			self.all_students = []

		selected_level = self.level_var.get() or ""
		selected_dept_label = getattr(self, "dept_var", None).get() if hasattr(self, "dept_var") else "Tous"
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

		# sélectionner le premier étudiant si dispo
		if self.filtered_students:
			self.student_listbox.selection_set(0)

		self.refresh_notes()

	# --- Utilitaire : récupérer l'étudiant sélectionné ---
	def get_selected_student(self):
		sel = self.student_listbox.curselection()
		if not sel:
			return None
		idx = sel[0]
		if idx < 0 or idx >= len(self.filtered_students):
			return None
		return self.filtered_students[idx]

	# --- Chargement des notes pour l'étudiant sélectionné ---
	def refresh_notes(self):
		for r in self.table.get_children():
			self.table.delete(r)

		student = self.get_selected_student()
		if not student:
			self._current_notes_filtered = []
			return

		try:
			all_notes = self.note_controller.read_all()
		except Exception:
			all_notes = []

		matricule = student.get("matricule", "")
		result = []
		for n in all_notes:
			if not isinstance(n, dict):
				continue
			if n.get("matricule") != matricule:
				continue
			result.append(n)

		for idx, item in enumerate(result):
			row_values = []
			for f in self.fields:
				val = item.get(f, "")
				if f == "typeEvaluation":
					val = self._to_display_type(val)
				row_values.append(val)
			self.table.insert("", "end", iid=str(idx), values=row_values)

		self._current_notes_filtered = result

	# --- Callback sélection étudiant ---
	def on_student_select(self):
		self.refresh_notes()

	def _to_display_type(self, raw_type: str) -> str:
		"""Convertit les codes internes (cot/cc/tp/ex) en libellés d'affichage CC/TP/EX."""
		if raw_type is None:
			return ""
		val = str(raw_type).strip()
		low = val.lower()
		if low in ("cot", "cc"):
			return "CC"
		if low == "tp":
			return "TP"
		if low == "ex":
			return "EX"
		return val

	# --- CRUD Notes ---
	def open_create_form(self):
		student = self.get_selected_student()
		if not student:
			messagebox.showinfo("Info", "Sélectionnez d'abord un étudiant.")
			return
		self._open_form(mode="create")

	def open_edit_form(self):
		student = self.get_selected_student()
		if not student:
			messagebox.showinfo("Info", "Sélectionnez d'abord un étudiant.")
			return
		sel = self.table.selection()
		if not sel:
			messagebox.showinfo("Info", "Sélectionnez une note à modifier.")
			return
		index = int(sel[0])
		try:
			data = self._current_notes_filtered[index]
		except Exception:
			data = {}
		self._open_form(mode="edit", data=data, index=index)

	def _open_form(self, mode="create", data=None, index=None):
		data = data or {}
		student = self.get_selected_student()
		if not student:
			messagebox.showinfo("Info", "Sélectionnez d'abord un étudiant.")
			return

		top = tk.Toplevel(self.master)
		top.title("Note - " + ("Créer" if mode == "create" else "Modifier"))
		top.transient(self.master)
		top.grab_set()

		form_frame = tk.Frame(top)
		form_frame.pack(padx=12, pady=12)

		# Matière
		tk.Label(form_frame, text="Matière").grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(4, 0))
		matiere_var = tk.StringVar()
		default_matiere = ""
		if mode == "edit":
			code_exist = data.get("code_matiere", "")
			nom_exist = data.get("nom_matiere", "")
			for label, info in self.matiere_display_to_data.items():
				if info.get("code_matiere") == code_exist or info.get("nom_matiere") == nom_exist:
					default_matiere = label
					break
		elif self.matiere_choices:
			default_matiere = self.matiere_choices[0]
		matiere_var.set(default_matiere)
		matiere_cb = ttk.Combobox(form_frame, textvariable=matiere_var, values=self.matiere_choices, width=30, state="readonly")
		matiere_cb.grid(row=1, column=0, sticky="we", pady=(0, 4))

		# Type d'évaluation (lié aux coefficients CC/TP/EX de la matière)
		tk.Label(form_frame, text="Type évaluation").grid(row=2, column=0, sticky="w", padx=(0, 6), pady=(4, 0))
		default_type_raw = data.get("typeEvaluation", "") if isinstance(data, dict) else ""
		default_type = self._to_display_type(default_type_raw)
		if default_type not in self.TYPE_EVAL:
			default_type = self.TYPE_EVAL[0]
		type_var = tk.StringVar(value=default_type)
		type_cb = ttk.Combobox(form_frame, textvariable=type_var, values=self.TYPE_EVAL, width=10, state="readonly")
		type_cb.grid(row=3, column=0, sticky="w", pady=(0, 4))

		# Valeur de la note
		tk.Label(form_frame, text="Note").grid(row=4, column=0, sticky="w", padx=(0, 6), pady=(4, 0))
		valeur_var = tk.StringVar(value=str(data.get("valeur", "")))
		valeur_ent = tk.Entry(form_frame, textvariable=valeur_var, width=10)
		valeur_ent.grid(row=5, column=0, sticky="w", pady=(0, 4))

		# Niveau (affiché en lecture seule)
		niveau_etud = student.get("niveau", "")
		tk.Label(form_frame, text="Niveau étudiant").grid(row=6, column=0, sticky="w", padx=(0, 6), pady=(4, 0))
		tk.Label(form_frame, text=niveau_etud).grid(row=7, column=0, sticky="w", pady=(0, 4))

		btns = tk.Frame(top)
		btns.pack(pady=(0, 12))

		def save_and_close():
			matiere_label = matiere_var.get()
			matiere_info = self.matiere_display_to_data.get(matiere_label, {"code_matiere": "", "nom_matiere": ""})

			# Construire l'objet note
			try:
				val = float(valeur_var.get().strip())
			except ValueError:
				messagebox.showerror("Erreur", "La note doit être un nombre.")
				return

			try:
				all_notes = self.note_controller.read_all()
			except Exception:
				all_notes = []

			if mode == "create":
				new_id = len(all_notes) + 1
			else:
				new_id = data.get("idNote", 0)
				if not new_id:
					new_id = len(all_notes) + 1

			obj = {
				"idNote": new_id,
				"valeur": val,
				"typeEvaluation": type_var.get().strip(),
				"niveau": niveau_etud,
				"matricule": student.get("matricule", ""),
				"code_matiere": matiere_info.get("code_matiere", ""),
				"nom_matiere": matiere_info.get("nom_matiere", ""),
			}

			if mode == "create":
				self.note_controller.create(obj)
			else:
				# retrouver l'indice global dans la liste du contrôleur
				try:
					all_notes = self.note_controller.read_all()
					target = self._current_notes_filtered[index]
					global_idx = all_notes.index(target)
				except Exception:
					global_idx = None
				if global_idx is not None:
					self.note_controller.update(global_idx, obj)

			self.refresh_notes()
			top.destroy()

		tk.Button(btns, text="Sauvegarder", command=save_and_close).pack(side=tk.LEFT, padx=6)
		tk.Button(btns, text="Annuler", command=top.destroy).pack(side=tk.LEFT)

		self.center_window(top, 520, 260)
		top.wait_window(top)

	def delete_note(self):
		student = self.get_selected_student()
		if not student:
			messagebox.showinfo("Info", "Sélectionnez d'abord un étudiant.")
			return
		sel = self.table.selection()
		if not sel:
			messagebox.showinfo("Info", "Sélectionnez une note à supprimer.")
			return
		index = int(sel[0])
		if not messagebox.askyesno("Confirmer", "Supprimer la note sélectionnée ?"):
			return

		try:
			all_notes = self.note_controller.read_all()
		except Exception:
			all_notes = []

		target = self._current_notes_filtered[index]
		try:
			global_idx = all_notes.index(target)
		except ValueError:
			global_idx = None

		if global_idx is not None:
			self.note_controller.delete(global_idx)
			self.refresh_notes()

	# --- Centrage fenêtre (repris de CRUDView) ---
	def center_window(self, window, width, height):
		self.master.update_idletasks()
		mw = self.master.winfo_width()
		mh = self.master.winfo_height()
		mx = self.master.winfo_rootx()
		my = self.master.winfo_rooty()
		if mw == 1 and mh == 1:
			sw = window.winfo_screenwidth()
			sh = window.winfo_screenheight()
			x = (sw - width) // 2
			y = (sh - height) // 2
		else:
			x = mx + (mw - width) // 2
			y = my + (mh - height) // 2
		window.geometry(f"{width}x{height}+{x}+{y}")
