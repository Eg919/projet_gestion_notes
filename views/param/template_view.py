import tkinter as tk
from tkinter import ttk, messagebox

from config.ui_theme import UI_FONT, UI_FONT_BOLD

# Largeurs de colonnes par défaut (en caractères) pour les champs courants
DEFAULT_COLUMN_WIDTH = 140
FIELD_WIDTHS = {
    "nom_departement": 220,
    "sigle_departement": 120,
    "code_matiere": 100,
    "nom_matiere": 200,
    "coefficient": 90,
    "coefficient_cc": 90,
    "coefficient_tp": 90,
    "coefficient_ex": 90,
}


def _apply_table_style(style_name="Crud"):
    """Applique un style moderne aux Treeview (entêtes, lignes, police)."""
    style = ttk.Style()
    style.configure(
        f"{style_name}.Treeview",
        font=UI_FONT,
        rowheight=28,
        fieldbackground="white",
    )
    style.configure(
        f"{style_name}.Treeview.Heading",
        font=UI_FONT_BOLD,
        padding=(8, 6),
    )
    style.map(f"{style_name}.Treeview", background=[("selected", "#0078d4")])


class CRUDView(tk.Frame):
    def __init__(self, master, controller, fields):
        super().__init__(master)
        self.master = master
        self.controller = controller
        self.fields = fields

        self.pack(fill=tk.BOTH, expand=True)

        # --- Frame pour les boutons ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=12, pady=10)

        self.add_btn = ttk.Button(btn_frame, text="Ajouter", command=self.open_create_form)
        self.add_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.edit_btn = ttk.Button(btn_frame, text="Modifier", command=self.open_edit_form)
        self.edit_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.del_btn = ttk.Button(btn_frame, text="Supprimer", command=self.delete)
        self.del_btn.pack(side=tk.LEFT)

        # --- Conteneur table + scrollbars ---
        table_container = tk.Frame(self)
        table_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        _apply_table_style("Crud")
        self.table = ttk.Treeview(
            table_container,
            columns=self.fields,
            show="headings",
            style="Crud.Treeview",
            selectmode="browse",
            height=18,
        )
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.table.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        for f in self.fields:
            width = FIELD_WIDTHS.get(f, DEFAULT_COLUMN_WIDTH)
            self.table.heading(f, text=f.replace("_", " ").title())
            self.table.column(f, width=width, minwidth=60, anchor="center")
        self.table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

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
            label_text = field.replace("_", " ").strip().title()
            tk.Label(form_frame, text=label_text, font=UI_FONT).grid(row=row_label, column=0, sticky="w", padx=(0, 8), pady=(6, 0))
            var = tk.StringVar(value=str(data.get(field, "")) if isinstance(data, dict) else "")
            ent = tk.Entry(form_frame, textvariable=var, width=42, font=UI_FONT)
            ent.grid(row=row_entry, column=0, sticky="we", pady=(0, 6))
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

        ttk.Button(btns, text="Sauvegarder", command=save_and_close).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Annuler", command=top.destroy).pack(side=tk.LEFT)

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

    # --- Centrer une fenêtre par rapport à la fenêtre principale ---
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



