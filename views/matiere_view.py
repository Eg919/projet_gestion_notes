from views.template_view import CRUDView
from controllers.matiere_controller import MatiereController

class MatiereView(CRUDView):
    def __init__(self, master):
        fields = [
            "code_matiere",
            "nom_matiere",
            "coefficient",
			"coefficient_cc",
            "coefficient_tp",
            "coefficient_ex"
        ]
        controller = MatiereController()
        super().__init__(master, controller, fields)
