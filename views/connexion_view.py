import tkinter as tk
from tkinter import ttk, messagebox

from config.auth_config import load_credentials
from config.ui_theme import UI_FONT, UI_FONT_ENTRY, UI_FONT_TITLE


class ConnexionView(tk.Toplevel):
	"""Fenêtre de connexion.

	Identifiants chargés dans cet ordre :
	1. Variables d'environnement : GESTION_NOTES_USER, GESTION_NOTES_PASSWORD
	2. Fichier protégé : config/credentials.json (à ne pas versionner)
	3. Valeurs par défaut (développement uniquement)
	"""

	def __init__(self, master, on_success=None):
		super().__init__(master)
		self.master = master
		self.on_success = on_success
		self._username, self._password = load_credentials()

		self.title("Connexion - Gestion des notes")
		self.resizable(False, False)

		container = tk.Frame(self, padx=24, pady=24)
		container.pack(fill=tk.BOTH, expand=True)

		# Titre (centré)
		title = tk.Label(container, text="Gestion des notes", font=UI_FONT_TITLE)
		title.pack(anchor="center", pady=(0, 20))

		# Nom d'utilisateur (centré)
		username_label = tk.Label(container, text="Nom d'utilisateur", font=UI_FONT)
		username_label.pack(anchor="center", pady=(0, 4))
		self.username_var = tk.StringVar()
		username_entry = tk.Entry(container, textvariable=self.username_var, width=28, font=UI_FONT_ENTRY)
		username_entry.pack(anchor="center", pady=(0, 12))

		# Mot de passe (centré)
		password_label = tk.Label(container, text="Mot de passe", font=UI_FONT)
		password_label.pack(anchor="center", pady=(0, 4))
		self.password_var = tk.StringVar()
		password_entry = tk.Entry(container, textvariable=self.password_var, show="*", width=28, font=UI_FONT_ENTRY)
		password_entry.pack(anchor="center", pady=(0, 20))

		# Boutons (centrés)
		btn_frame = tk.Frame(container)
		btn_frame.pack(anchor="center", pady=(0, 4))

		login_btn = ttk.Button(btn_frame, text="Connexion", command=self._attempt_login)
		login_btn.pack(side=tk.LEFT, padx=(0, 8))

		cancel_btn = ttk.Button(btn_frame, text="Annuler", command=self._cancel)
		cancel_btn.pack(side=tk.LEFT)

		# Validation par Entrée
		self.bind("<Return>", lambda e: self._attempt_login())

		self.grab_set()
		self._center_window(360, 280)
		username_entry.focus_set()
		self.protocol("WM_DELETE_WINDOW", self._cancel)

	def _center_window(self, width, height):
		self.update_idletasks()
		sw = self.winfo_screenwidth()
		sh = self.winfo_screenheight()
		x = (sw - width) // 2
		y = (sh - height) // 2
		self.geometry(f"{width}x{height}+{x}+{y}")

	def _attempt_login(self):
		username = self.username_var.get().strip()
		password = self.password_var.get().strip()

		if username == self._username and password == self._password:
			# Succès : fermer la fenêtre et lancer le callback
			self.destroy()
			if callable(self.on_success):
				self.on_success()
		else:
			messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

	def _cancel(self):
		"""Annuler la connexion : fermer l'application principale."""
		self.destroy()
		if self.master is not None:
			self.master.destroy()
