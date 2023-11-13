from typing import Callable, Optional
from PySide6.QtWidgets import QMainWindow, QGraphicsRectItem
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt

class customWindow(QMainWindow):
    """
    This class object is a custom QMainWindow implementation
    """
    def __init__(self, logger: Optional['logging.Logger'] = None):
        """
        Constructor of the class.
        
        Arguments:
            - logger (Optional[logging.Logger]): The logger instance from the `logging`
                module. Default is None.
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
        if hasattr(self, 'selectionStarPoint') and hasattr(self,
                    'selectionEndPoint'):
            x=self.selectionStarPoint.x()
            y=self.selectionStarPoint.y()
            width = self.selectionEndPoint.x()-x
            height = self.selectionEndPoint.y()-y
            print(x, y, width, height)
            painter.drawRect(x, y, width, height)
            painter.end()
        else:
            self._tryLogger_('...no selection rect has been defined yet...')
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selectionStarPoint = event.pos()
            self.update()
            
    def mouseMoveEvent(self, event):
        self.selectionEndPoint = event.pos()
        self.update()

    # def mouseReleaseEvent(self, event):
    #     self.selectionEndPosition = event.pos()
    #     self.update()
    def _tryLogger_(self, log: [str]):
        try:
            self.logger.debug(log)
        except Exception as e:
            print(f'Error writing log: {e} continuing with simple print\n{log}')

