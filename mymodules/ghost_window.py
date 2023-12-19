from typing import Optional, Literal
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt, QSize, QPoint, Signal
import pywinctl
from PIL import ImageGrab
from logging import Logger

size: QSize
thisLogger: Logger | None

class MyQtApp(QApplication):
    def __init__(self, logger: Optional['Logger'] = None) -> None:
        super().__init__()
        global thisLogger
        thisLogger = logger
        global size
        size = self.primaryScreen().size()
        _tryLogger_(log=f'Primary screen size: {size.width(), size.height()}')
    
    # def run(self) -> int:
    #     super().exec()
    #     while self.appWindow.watchdog.isAlive():
    #         self.processEvents()
    #     self._tryLogger_('QApplication terminated')
    #     return 0
    
class CustomWindow(QMainWindow):
    """
    This class object is a custom QMainWindow implementation
    """
    def __init__(self, appWindow: pywinctl.Window, screenShotsPath: str | None):
        """
        Constructor of the class.
        
        Arguments:
            - logger (Optional[logging.Logger]): The logger instance from the `logging`
                module. Default is None.
        """
        super().__init__()
        self.appWindow = appWindow
        self.screenShotsPath = screenShotsPath
        self.setWindowTitle('Pixel ghost window')
        self.setAttribute(Qt.WA_NoSystemBackground, on=True)
        self.setAttribute(Qt.WA_TranslucentBackground, on=True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.drawGhostWindow()
        self.selectionStarPoint: QPoint | None = None
        self.selectionEndPoint: QPoint | None = None
        self.segnale = Signal(int)
    
    def paintEvent(self, event=None):
        # super().paintEvent(event)
        if event is not None:
            print(event.type())
            with QPainter(self) as painter:
                painter.setOpacity(0.5)
                painter.setBrush(Qt.black)
                painter.setPen(QPen(Qt.white))
                painter.drawRect(self.rect())
                # if hasattr(self, 'selectionStarPoint') and hasattr(self, 'selectionEndPoint'):
                if self.selectionStarPoint is not None and self.selectionEndPoint is not None:
                    x = self.selectionStarPoint.x()
                    y = self.selectionStarPoint.y()
                    # top = self.selectionEndPoint.x()
                    # bottom = self.selectionEndPoint.y()
                    width = self.selectionEndPoint.x()-x
                    height = self.selectionEndPoint.y()-y
                    painter.setCompositionMode(QPainter.CompositionMode_Clear)
                    painter.drawRect(x, y, width, height)
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                else:
                    _tryLogger_(log='...no selection rect has been defined yet...')
                # if painter.isActive():
                #     painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selectionStarPoint = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        left = self.geometry().x()+self.selectionStarPoint.x()
        top = self.geometry().y()+self.selectionStarPoint.y()
        right = self.geometry().x()+self.selectionEndPoint.x()
        bottom = self.geometry().y()+self.selectionEndPoint.y()
        bbox = left, top, right, bottom
        screenshot = ImageGrab.grab(bbox)
        screenshot.save(f"{self.screenShotsPath}/screenshot.png")
        screenshot.show()
        
    def mouseMoveEvent(self, event):
        self.selectionEndPoint = event.pos()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_H:
            if self.isVisible():
                self.showMinimized()
            else:
                self.show()
        else:
            pass

    def drawGhostWindow(self, redraw=False) -> None:  # redraw is mandatory
        # to watchdog, to know if is first draw or redraw after move
        # or resize.
        resolution: dict[str, int] = {'width': size.width(), 'height': size.height()}
        left, top, right, bottom = self.appWindow.bbox
        if left < 0:
            width = right
        else:
            width = right-left
        if right > resolution.get('width'):
            width = resolution.get('width')-left
        if bottom > resolution.get('height'):
            height = resolution.get('height')-top
        else:
            height = bottom-top
        self.setGeometry(left, top, width, height)
        if redraw:
            _tryLogger_(log='Redrawing ghost window after moving or resizing', level='debug')
        else:
            _tryLogger_(log='Drawing ghost window for first time', level='debug')
        self.show()

    # def mouseReleaseEvent(self, event):
    #     self.selectionEndPosition = event.pos()
    #     self.update()
    
def _tryLogger_(log: str, level: Literal['debug', 'info', 'error', 'critical']
                = 'debug'):
    try:
        log_method = getattr(thisLogger, level)
        log_method(log)
    except Exception as e:
        print(f"Error writing log: {e} "
                f"continuing with simple print\n{log}")
