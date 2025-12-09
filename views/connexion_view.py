import tkinter as tk
from tkinter import ttk, messagebox


class ConnexionView(tk.Toplevel):
	"""Petite fenêtre de connexion simple.

	Identifiants fixes :
	- Nom d'utilisateur : Admin
	- Mot de passe     : 1234
	"""

	USERNAME = "Admin"
	PASSWORD = "1234"

	def __init__(self, master, on_success=None):
		super().__init__(master)
		self.master = master
		self.on_success = on_success

		self.title("Connexion")
		self.resizable(False, False)

		container = tk.Frame(self)
		container.pack(padx=20, pady=20)

		# Nom d'utilisateur
		username_label = tk.Label(container, text="Nom d'utilisateur")
		username_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
		self.username_var = tk.StringVar()
		username_entry = tk.Entry(container, textvariable=self.username_var, width=25)
		username_entry.grid(row=1, column=0, sticky="we", pady=(0, 8))

		# Mot de passe
		password_label = tk.Label(container, text="Mot de passe")
		password_label.grid(row=2, column=0, sticky="w", pady=(0, 4))
		self.password_var = tk.StringVar()
		password_entry = tk.Entry(container, textvariable=self.password_var, show="*", width=25)
		password_entry.grid(row=3, column=0, sticky="we", pady=(0, 12))

		# Boutons
		btn_frame = tk.Frame(container)
		btn_frame.grid(row=4, column=0, pady=(0, 4))

		login_btn = tk.Button(btn_frame, text="Connexion", command=self._attempt_login)
		login_btn.pack(side=tk.LEFT, padx=(0, 6))

		cancel_btn = tk.Button(btn_frame, text="Annuler", command=self._cancel)
		cancel_btn.pack(side=tk.LEFT)

		# Validation par Entrée
		self.bind("<Return>", lambda e: self._attempt_login())

		self.grab_set()
		self._center_window(320, 200)
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

		if username == self.USERNAME and password == self.PASSWORD:
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
