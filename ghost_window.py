from typing import Callable, Optional, Literal
from PySide6.QtWidgets import QMainWindow, QGraphicsRectItem, QApplication
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt
import pywinctl

class myQtApp(QApplication):
    def __init__(self):
        super().__init__()
        global size
        size=self.primaryScreen().size().toTuple()

    def exec(self, appWindow: pywinctl.Window):
        while appWindow.watchdog.isAlive():
            self.processEvents()
        self._tryLogger_('QApplication terminated')
        return 0
    
    def _tryLogger_(self, log: str, level: Literal['debug', 'info', 'error'] = 
                    'debug'):
        try:
            log_method = getattr(self.logger, level)
            log_method(log)
        except Exception as e:
            print(f'Error writing log: {e} '
                    f'continuing with simple print\n{log}')

class customWindow(QMainWindow):
    """
    This class object is a custom QMainWindow implementation
    """
    def __init__(self, appWindow: pywinctl.Window, logger: Optional['logging.Logger'] = None):
        """
        Constructor of the class.
        
        Arguments:
            - logger (Optional[logging.Logger]): The logger instance from the `logging`
                module. Default is None.
        """
        super().__init__()
        self.appWindow = appWindow
        self.logger = logger
        self.setWindowTitle('Pixel ghost window')
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.drawGhostWindow()
        
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

    def drawGhostWindow(self, resolution = None, redraw = False): # redraw is mandatory 
        # to watchdog, to know if is first draw or redraw after move
        # or resize.
        resolution={'width':size[0],'height':size[1]}
        left, top, right, bottom = self.appWindow.bbox
        if left<0:
            width=right
        else:
            width=right-left
        if right>resolution.get('width'):
            width=resolution.get('width')-left
        if bottom>resolution.get('height'):
            height=resolution.get('height')-top
        else:
            height=bottom-top
        self.setGeometry(left,top,width,height)
        if redraw:
            self.logger.debug('Redrawing ghost window after moving or '
                                f'resizing')
        else:
            self.logger.debug('Drawing ghost window for first time')
        self.show()

    # def mouseReleaseEvent(self, event):
    #     self.selectionEndPosition = event.pos()
    #     self.update()
    
    def _tryLogger_(self, log: str, level: Literal['debug', 'info', 'error'] = 
                    'debug'):
        try:
            log_method = getattr(self.logger, level)
            log_method(log)
        except Exception as e:
            print(f'Error writing log: {e} '
                    f'continuing with simple print\n{log}')


