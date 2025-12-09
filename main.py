import tkinter as tk
from tkinter import ttk

# Import des vues
from views.departement_view import DepartementView
from views.matiere_view import MatiereView
from views.views.etudiant_view import EtudiantView
from views.views.note_view import NoteView

# --- Création de la fenêtre principale ---
root = tk.Tk()
root.title("Gestion des Notes - Université")

# --- Taille et centrage de la fenêtre ---
width, height = 1024, 768
root.geometry(f"{width}x{height}")
root.update_idletasks()
x = (root.winfo_screenwidth() - width) // 2
y = (root.winfo_screenheight() - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")
root.minsize(800, 600)

# --- Création du notebook pour les onglets ---
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# --- Ajout des onglets ---
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


# Rafraîchir certaines vues lors du changement d'onglet
def on_tab_changed(event):
	selected = event.widget.select()
	tab = event.widget.nametowidget(selected)
	# Quand on arrive sur l'onglet Notes, recharger la liste des étudiants
	if tab is note_tab:
		note_tab.refresh_students_list()


notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# --- Boucle principale ---
root.mainloop()
