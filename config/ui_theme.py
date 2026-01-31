"""
Thème UI : police et constantes d'affichage.

Utilise "Segoe UI" sur Windows si disponible, sinon une police de repli
(TkDefaultFont, etc.) pour Linux/macOS.
"""
import tkinter.font as tkfont

# Détection de la police : Segoe UI (Windows) ou repli
try:
    _families = set(tkfont.families())
    if "Segoe UI" in _families:
        FONT_FAMILY = "Segoe UI"
    elif "Helvetica" in _families:
        FONT_FAMILY = "Helvetica"
    else:
        FONT_FAMILY = "TkDefaultFont"
except Exception:
    FONT_FAMILY = "TkDefaultFont"

# Polices prédéfinies pour les vues
UI_FONT = (FONT_FAMILY, 10)
UI_FONT_BOLD = (FONT_FAMILY, 10, "bold")
UI_FONT_TITLE = (FONT_FAMILY, 14, "bold")
UI_FONT_ENTRY = (FONT_FAMILY, 11)
