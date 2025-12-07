from controllers.base_controller import BaseController

class NoteController(BaseController):
    def __init__(self):
        super().__init__("notes.json")
