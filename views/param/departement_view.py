import tkinter as tk
from controllers.departement_controller import DepartementController
from views.param.template_view import CRUDView

class DepartementView(CRUDView):
    def __init__(self, master):
        fields = ["nom_departement", "sigle_departement"]
        controller = DepartementController()
        super().__init__(master, controller, fields)
