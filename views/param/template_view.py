import tkinter as tk
from tkinter import ttk, messagebox

class CRUDView(tk.Frame):
    def __init__(self, master, controller, fields):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.fields = fields

        # --- Pack général du Fenetre ---
        self.pack(fill=tk.BOTH, expand=True)

        # --- Frame pour les boutons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=8)

        self.add_btn = tk.Button(btn_frame, text="Ajouter", command=self.open_create_form)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.edit_btn = tk.Button(btn_frame, text="Modifier", command=self.open_edit_form)
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.del_btn = tk.Button(btn_frame, text="Supprimer", command=self.delete)
        self.del_btn.pack(side=tk.LEFT)

        # --- Table principale ---
        # Style avec entêtes en gras (pas de bordures spéciales pour éviter les erreurs)
        style = ttk.Style()
        style.configure("Crud.Treeview.Heading", font=("TkDefaultFont", 10, "bold"))
        self.table = ttk.Treeview(self, columns=self.fields, show="headings", style="Crud.Treeview")
        for f in self.fields:
            self.table.heading(f, text=f)
            self.table.column(f, width=120, anchor="center")
        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Rafraîchir la table pour afficher les données existantes
        self.refresh_table()

    # --- Rafraîchissement de la table ---
    def refresh_table(self):
        for row in self.table.get_children():
            self.table.delete(row)
        try:
            items = self.controller.read_all()  # <-- correction ici
        except Exception:
            items = []
        for idx, item in enumerate(items):
            if isinstance(item, dict):
                values = [item.get(f, "") for f in self.fields]
            else:
                values = [str(item)] + [""] * (len(self.fields) - 1)
            self.table.insert("", "end", iid=str(idx), values=values)

    # --- Formulaire Ajouter ---
    def open_create_form(self):
        self._open_form(mode="create")

    # --- Formulaire Modifier ---
    def open_edit_form(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo("Info", "Sélectionnez un élément à modifier.")
            return
        index = int(sel[0])
        try:
            items = self.controller.read_all()  # <-- correction ici
            data = items[index]
        except Exception:
            data = {}
        self._open_form(mode="edit", data=data, index=index)

    # --- Formulaire générique ---
    def _open_form(self, mode="create", data=None, index=None):
        data = data or {}
        top = tk.Toplevel(self.master)
        top.title("Formulaire - " + ("Créer" if mode=="create" else "Modifier"))
        top.transient(self.master)
        top.grab_set()  # modal

        form_frame = tk.Frame(top)
        form_frame.pack(padx=12, pady=12)

        entries = {}
        for i, field in enumerate(self.fields):
            row_label = 2 * i
            row_entry = row_label + 1
            # Label au-dessus du champ de saisie
            tk.Label(form_frame, text=field).grid(row=row_label, column=0, sticky="w", padx=(0,6), pady=(4, 0))
            var = tk.StringVar(value=str(data.get(field, "")) if isinstance(data, dict) else "")
            ent = tk.Entry(form_frame, textvariable=var, width=40)
            ent.grid(row=row_entry, column=0, sticky="we", pady=(0, 4))
            entries[field] = var

        btns = tk.Frame(top)
        btns.pack(pady=(0,12))

        def save_and_close():
            obj = {k: v.get().strip() for k, v in entries.items()}
            try:
                if mode == "create":
                    self.controller.create(obj)
                else:
                    self.controller.update(index, obj)
                self.refresh_table()
                top.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec de l'opération : {e}")

        tk.Button(btns, text="Sauvegarder", command=save_and_close).pack(side=tk.LEFT, padx=6)
        tk.Button(btns, text="Annuler", command=top.destroy).pack(side=tk.LEFT)

        # Centrer le formulaire
        height = (len(self.fields) * 30) + 140
        # Pour les formulaires avec beaucoup de champs (ex : matières),
        # on ajoute de la hauteur pour plus de confort.
        if len(self.fields) >= 6:
            height += 120
        self.center_window(top, 480, height)
        top.wait_window(top)

    # --- Supprimer un élément ---
    def delete(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showerror("Erreur", "Sélectionner un élément")
            return
        index = int(sel[0])
        if not messagebox.askyesno("Confirmer", "Supprimer l'élément sélectionné ?"):
            return
        try:
            self.controller.delete(index)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer : {e}")

    # --- Centrer une fenêtre ---
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



