import tkinter as tk
from tkinter import ttk

# Import des vues
from views.param.departement_view import DepartementView
from views.param.matiere_view import MatiereView
from views.param.etudiant_view import EtudiantView
from views.note_view import NoteView
from views.bulletin_view import BulletinView
from views.connexion_view import ConnexionView


def build_main_ui(root: tk.Tk):
	"""Construit le notebook principal avec tous les onglets."""
	notebook = ttk.Notebook(root)
	notebook.pack(fill="both", expand=True)

	# Onglet Départements
	departement_tab = DepartementView(notebook)
	notebook.add(departement_tab, text="Départements")
	# Onglet Matières
	matiere_tab = MatiereView(notebook)
	notebook.add(matiere_tab, text="Matières")
	# Onglet Étudiants
	etudiant_tab = EtudiantView(notebook)
	notebook.add(etudiant_tab, text="Étudiants")

	# Onglet Notes
	note_tab = NoteView(notebook)
	notebook.add(note_tab, text="Notes")

	# Onglet Bulletin
	bulletin_tab = BulletinView(notebook)
	notebook.add(bulletin_tab, text="Bulletin")

	# Rafraîchir certaines vues lors du changement d'onglet
	def on_tab_changed(event):
		selected = event.widget.select()
		tab = event.widget.nametowidget(selected)
		# Quand on arrive sur l'onglet Notes ou Bulletin, recharger la liste des étudiants
		if tab is note_tab:
			note_tab.refresh_students_list()
		elif tab is bulletin_tab:
			bulletin_tab.refresh_students_list()
			bulletin_tab.refresh_bulletin()

	notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

	return notebook


if __name__ == "__main__":
	# --- Création de la fenêtre principale ---
	root = tk.Tk()
	root.title("Gestion des Notes - Université")

	# --- Taille et centrage de la fenêtre principale ---
	width, height = 1024, 768
	root.geometry(f"{width}x{height}")
	root.update_idletasks()
	x = (root.winfo_screenwidth() - width) // 2
	y = (root.winfo_screenheight() - height) // 2
	root.geometry(f"{width}x{height}+{x}+{y}")
	root.minsize(800, 600)

	# On cache la fenêtre principale tant que la connexion n'est pas validée
	root.withdraw()

	def start_app():
		"""Callback appelé après une connexion réussie."""
		# Construire l'UI principale une seule fois
		if not getattr(root, "_app_built", False):
			build_main_ui(root)
			root._app_built = True
		# Afficher la fenêtre principale
		root.deiconify()

	# Afficher la fenêtre de connexion
	ConnexionView(root, on_success=start_app)

	# --- Boucle principale ---
	root.mainloop()
