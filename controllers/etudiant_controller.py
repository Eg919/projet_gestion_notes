from controllers.base_controller import BaseController

class EtudiantController(BaseController):
    def __init__(self):
        super().__init__("etudiants.json")
