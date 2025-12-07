from controllers.base_controller import BaseController

class DepartementController(BaseController):
    def __init__(self):
        super().__init__("departements.json")
