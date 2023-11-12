from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt

class customWindow(QMainWindow):
    """
    This class object is a custom QMainWindow implementation
    """
    def __init__(self):
        """
        Constructor of the class.
        """
        super().__init__()
        self.setWindowTitle('Pixel ghost window')
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
    def paintEvent(self, event=None):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setOpacity(0.5)
        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.white))   
        painter.drawRect(self.rect())
