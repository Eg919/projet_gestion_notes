import tkinter as tk
from tkinter import ttk, messagebox

from config.ui_theme import UI_FONT, UI_FONT_BOLD
from controllers.departement_controller import DepartementController
from controllers.etudiant_controller import EtudiantController
from controllers.note_controller import NoteController
from views.param.template_view import CRUDView


class EtudiantView(tk.Frame):
	"""Onglet de gestion des étudiants.

	- Bandeau haut : boutons Ajouter / Modifier / Supprimer
	  + filtre par niveau (L1, L2, L3, M1, M2, D).
	- Zone centrale :
		* colonne gauche (20%) : liste des départements
		* colonne droite (80%) : table des étudiants du département sélectionné,
		  filtrée par niveau si sélectionné.
	"""

	NIVEAUX = ["", "L1", "L2", "L3", "M1", "M2", "D"]

	def __init__(self, master):
		super().__init__(master)
		self.master = master

		self.departement_controller = DepartementController()
		self.etudiant_controller = EtudiantController()
		self.note_controller = NoteController()

		self.selected_departement_index = None

		self.pack(fill=tk.BOTH, expand=True)

		# --- Bandeau de commandes haut ---
		top_bar = tk.Frame(self)
		top_bar.pack(fill=tk.X, padx=12, pady=10)

		self.add_btn = ttk.Button(top_bar, text="Ajouter", command=self.open_create_form)
		self.add_btn.pack(side=tk.LEFT, padx=(0, 6))

		self.edit_btn = ttk.Button(top_bar, text="Modifier", command=self.open_edit_form)
		self.edit_btn.pack(side=tk.LEFT, padx=(0, 6))

		self.del_btn = ttk.Button(top_bar, text="Supprimer", command=self.delete_etudiant)
		self.del_btn.pack(side=tk.LEFT, padx=(0, 12))

		# Filtre par niveau
		tk.Label(top_bar, text="Filtrer par niveau :", font=UI_FONT).pack(side=tk.LEFT)
		self.level_var = tk.StringVar(value="")
		level_cb = ttk.Combobox(top_bar, textvariable=self.level_var, values=self.NIVEAUX, width=8, state="readonly")
		level_cb.pack(side=tk.LEFT, padx=(4, 0))
		level_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_students())

		# --- Zone centrale avec 2 colonnes ---
		center = tk.Frame(self)
		center.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

		center.columnconfigure(0, weight=1)
		center.columnconfigure(1, weight=4)
		center.rowconfigure(0, weight=1)

		# Liste des départements (gauche)
		left_frame = tk.LabelFrame(center, text=" Départements ", font=UI_FONT_BOLD, padx=6, pady=6)
		left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

		left_inner = tk.Frame(left_frame)
		left_inner.pack(fill=tk.BOTH, expand=True)
		self.dept_listbox = tk.Listbox(left_inner, exportselection=False, font=UI_FONT, height=20)
		left_sb = ttk.Scrollbar(left_inner, orient="vertical", command=self.dept_listbox.yview)
		self.dept_listbox.configure(yscrollcommand=left_sb.set)
		self.dept_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		left_sb.pack(side=tk.RIGHT, fill=tk.Y)
		self.dept_listbox.bind("<<ListboxSelect>>", lambda e: self.on_departement_select())

		# Table des étudiants (droite)
		right_frame = tk.LabelFrame(center, text=" Étudiants ", font=UI_FONT_BOLD, padx=6, pady=6)
		right_frame.grid(row=0, column=1, sticky="nsew")
		right_frame.grid_rowconfigure(0, weight=1)
		right_frame.grid_columnconfigure(0, weight=1)

		table_wrap = tk.Frame(right_frame)
		table_wrap.grid(row=0, column=0, sticky="nsew")
		table_wrap.grid_rowconfigure(0, weight=1)
		table_wrap.grid_columnconfigure(0, weight=1)

		self.fields = ["matricule", "nom", "prenom", "niveau"]
		style = ttk.Style()
		style.configure("Etudiant.Treeview", font=UI_FONT, rowheight=26)
		style.configure("Etudiant.Treeview.Heading", font=UI_FONT_BOLD, padding=(8, 6))
		style.map("Etudiant.Treeview", background=[("selected", "#0078d4")])
		self.table = ttk.Treeview(table_wrap, columns=self.fields, show="headings", style="Etudiant.Treeview", height=18, selectmode="browse")
		vsb = ttk.Scrollbar(table_wrap, orient="vertical", command=self.table.yview)
		hsb = ttk.Scrollbar(table_wrap, orient="horizontal", command=self.table.xview)
		self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
		for f in self.fields:
			w = 100 if f == "matricule" else (160 if f in ("nom", "prenom") else 70)
			self.table.heading(f, text=f.capitalize())
			self.table.column(f, width=w, minwidth=50, anchor="center")
		self.table.grid(row=0, column=0, sticky="nsew")
		vsb.grid(row=0, column=1, sticky="ns")
		hsb.grid(row=1, column=0, sticky="ew")

		# Charger les données
		self.refresh_departements()
		self.refresh_students()

	# --- Chargement départements ---
	def refresh_departements(self):
		self.dept_listbox.delete(0, tk.END)
		try:
			self.departements = self.departement_controller.read_all()
		except Exception:
			self.departements = []
		for idx, d in enumerate(self.departements):
			nom = d.get("nom_departement", "?") if isinstance(d, dict) else str(d)
			self.dept_listbox.insert(tk.END, nom)
		if self.departements:
			self.dept_listbox.selection_set(0)
			self.selected_departement_index = 0
		else:
			self.selected_departement_index = None

	# --- Chargement étudiants en fonction du département & niveau ---
	def refresh_students(self):
		for r in self.table.get_children():
			self.table.delete(r)

		try:
			etudiants = self.etudiant_controller.read_all()
		except Exception:
			etudiants = []

		selected_level = self.level_var.get() or ""

		# filtre par departement (stocké comme index ou sigle)
		dept_idx = self.selected_departement_index
		result = []
		for e in etudiants:
			if not isinstance(e, dict):
				continue

			# filtre niveau
			if selected_level and e.get("niveau") != selected_level:
				continue

			# filtre departement: on stockera l'index du département dans le champ "departement_index"
			if dept_idx is not None:
				if e.get("departement_index") != dept_idx:
					continue

			result.append(e)

		for idx, item in enumerate(result):
			values = [item.get(f, "") for f in self.fields]
			self.table.insert("", "end", iid=str(idx), values=values)

		self._current_filtered = result

	# --- Callback sélection département ---
	def on_departement_select(self):
		sel = self.dept_listbox.curselection()
		if not sel:
			self.selected_departement_index = None
		else:
			self.selected_departement_index = sel[0]
		self.refresh_students()

	# --- CRUD Étudiants ---
	def open_create_form(self):
		if self.selected_departement_index is None:
			messagebox.showinfo("Info", "Sélectionnez d'abord un département.")
			return
		self._open_form(mode="create")

	def open_edit_form(self):
		sel = self.table.selection()
		if not sel:
			messagebox.showinfo("Info", "Sélectionnez un étudiant à modifier.")
			return
		index = int(sel[0])
		try:
			data = self._current_filtered[index]
		except Exception:
			data = {}
		self._open_form(mode="edit", data=data, index=index)

	def _open_form(self, mode="create", data=None, index=None):
		data = data or {}
		top = tk.Toplevel(self.master)
		top.title("Étudiant - " + ("Créer" if mode == "create" else "Modifier"))
		top.transient(self.master)
		top.grab_set()

		form_frame = tk.Frame(top)
		form_frame.pack(padx=12, pady=12)

		fields = ["matricule", "nom", "prenom", "niveau"]
		entries = {}
		for i, field in enumerate(fields):
			row_label = 2 * i
			row_input = row_label + 1
			# Label au-dessus du champ de saisie
			tk.Label(form_frame, text=field.capitalize()).grid(row=row_label, column=0, sticky="w", padx=(0, 6), pady=(4, 0))

			if field == "niveau":
				var = tk.StringVar(value=data.get(field, ""))
				cb = ttk.Combobox(form_frame, textvariable=var, values=self.NIVEAUX[1:], width=10, state="readonly")
				cb.grid(row=row_input, column=0, sticky="w", pady=(0, 4))
				entries[field] = var
			else:
				var = tk.StringVar(value=str(data.get(field, "")) if isinstance(data, dict) else "")
				ent = tk.Entry(form_frame, textvariable=var, width=40)
				ent.grid(row=row_input, column=0, sticky="we", pady=(0, 4))
				entries[field] = var

		btns = tk.Frame(top)
		btns.pack(pady=(0, 12))

		def save_and_close():
			obj = {k: v.get().strip() for k, v in entries.items()}
			# lier automatiquement au département sélectionné
			obj["departement_index"] = self.selected_departement_index

			# Utiliser le contrôleur comme dans CRUDView
			if mode == "create":
				self.etudiant_controller.create(obj)
			else:
				# retrouver l'indice global dans la liste du contrôleur
				try:
					all_students = self.etudiant_controller.read_all()
					target = self._current_filtered[index]
					global_idx = all_students.index(target)
				except Exception:
					global_idx = None
				if global_idx is not None:
					self.etudiant_controller.update(global_idx, obj)

			self.refresh_students()
			top.destroy()

		ttk.Button(btns, text="Sauvegarder", command=save_and_close).pack(side=tk.LEFT, padx=6)
		ttk.Button(btns, text="Annuler", command=top.destroy).pack(side=tk.LEFT)

		self.center_window(top, 480, 260)
		top.wait_window(top)

	def delete_etudiant(self):
		sel = self.table.selection()
		if not sel:
			messagebox.showinfo("Info", "Sélectionnez un étudiant à supprimer.")
			return
		index = int(sel[0])
		if not messagebox.askyesno("Confirmer", "Supprimer l'étudiant sélectionné ?"):
			return

		try:
			all_students = self.etudiant_controller.read_all()
		except Exception:
			all_students = []

		target = self._current_filtered[index]
		try:
			global_idx = all_students.index(target)
		except ValueError:
			global_idx = None

		if global_idx is not None:
			# Conserver le matricule pour supprimer aussi les notes associées
			student = all_students[global_idx]
			matricule = student.get("matricule", "") if isinstance(student, dict) else ""

			# Supprimer l'étudiant via le contrôleur
			self.etudiant_controller.delete(global_idx)

			# Suppression en cascade des notes de cet étudiant
			try:
				all_notes = self.note_controller.read_all()
			except Exception:
				all_notes = []

			if matricule:
				new_notes = []
				for n in all_notes:
					if not isinstance(n, dict):
						new_notes.append(n)
						continue
					if n.get("matricule") != matricule:
						new_notes.append(n)

				# Mettre à jour le fichier des notes uniquement si nécessaire
				if len(new_notes) != len(all_notes):
					self.note_controller.data = new_notes
					self.note_controller.save()

			self.refresh_students()

	# --- Centrage fenêtre par rapport à la fenêtre principale ---
	def center_window(self, window, width, height):
		root = self.winfo_toplevel()
		root.update_idletasks()
		mw = root.winfo_width()
		mh = root.winfo_height()
		mx = root.winfo_rootx()
		my = root.winfo_rooty()
		if mw <= 1 or mh <= 1:
			sw = window.winfo_screenwidth()
			sh = window.winfo_screenheight()
			x = (sw - width) // 2
			y = (sh - height) // 2
		else:
			x = mx + (mw - width) // 2
			y = my + (mh - height) // 2
		window.geometry(f"{width}x{height}+{x}+{y}")

