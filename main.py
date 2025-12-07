import tkinter as tk
from tkinter import ttk

# Import des vues
from views.departement_view import DepartementView
from views.matiere_view import MatiereView
from views.views.etudiant_view import EtudiantView

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

# --- Boucle principale ---
root.mainloop()
