# /home/soutonnoma/PycharmProjects/HotelManager/ui/center_utils.py

from PySide6.QtWidgets import QApplication

def center_on_screen(widget):
    """
    Fonction utilitaire pour centrer n'importe quel widget/fenêtre sur l'écran principal.
    Doit être appelée APRÈS que le widget a été affiché avec. Show().
    """
    try:
        # Récupère le rectangle de l'écran avec lequel se trouve la fenêtre
        screen_geometry = widget.screen().geometry()
        # Récupère le rectangle de notre fenêtre
        widget_geometry = widget.frameGeometry()
        # Calcule le point central de l'écran et déplace notre fenêtre là-bas
        center_point = screen_geometry.center()
        widget_geometry.moveCenter(center_point)
        widget.move(widget_geometry.topLeft())
    except Exception as e:
        # Sécurité au cas où l'écran ne serait pas disponible
        print(f"Avertissement : Impossible de centrer la fenêtre. Erreur : {e}")
