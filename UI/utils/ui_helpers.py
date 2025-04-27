from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from config import COLOR_SHADOW

def add_shadow(widget, blur=25, dx=0, dy=3):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(blur)
    shadow.setOffset(dx, dy)
    shadow.setColor(COLOR_SHADOW)
    widget.setGraphicsEffect(shadow)
