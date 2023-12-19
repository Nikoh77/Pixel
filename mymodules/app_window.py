from typing import List, Optional, Literal
from mymodules.timer import Timer
import pywinctl
from logging import Logger
from PySide6.QtCore import QObject, Signal
from ghost_window import CustomWindow

testObj = QObject
testSign = Signal
thisLogger: Logger | None

class Window(pywinctl.Window):
    """
    This class object is a custom pywinctl window implementation
    """
    def __init__(self, wdOverrideInterval: Optional[float],
                 logger: Optional['Logger'] = None) -> None:
        """
        Constructor of the class.
        
        Arguments:
            - logger (Optional[logging.Logger]): The logger instance from the `logging`
                module. Default is None.
        """
        global thisLogger
        thisLogger = logger
        self.wdOverrideInterval = wdOverrideInterval
        self.hWnd: pywinctl.Window | int | str | None = self.whichWindow()
        if self.hWnd is not None: # TODO:  aggiungere un try
            super().__init__(hWnd=self.hWnd)

    def whichWindow(self) -> str | int | None:
        """
        In this function, active windows on the desktop are searched and listed for the
        user to choose which one Pixel should operate on.
        """
        try:
            apps: list[str] = pywinctl.getAllAppsNames()
            _tryLogger_(log=f'list of currently visible '
                        f'applications/windows: {apps}')
            x = -1
            while not (0 <= x <= len(apps)-1):
                print('Please choose which app you want to use with Pixel:')
                index = 0
                for app in apps:
                    print(index, app)
                    index += 1
                try:    
                    x = int(input())
                except ValueError:
                    print('Please choose a number...\n')
            app = apps[x]
            _tryLogger_(f'Application was chosen: {app}')
            wTitles: List[str] | None = pywinctl.getAllAppsWindowsTitles().get(app)
            if wTitles is not None:
                if len(wTitles) == 1:
                    # app has just one window
                    wTitle = wTitles[0]
                    appWindow = pywinctl.getWindowsWithTitle(title=wTitle)[0]
                    return appWindow.getHandle()
                else:
                    _tryLogger_(log=f'the selected app has more than one window: '
                                f'{wTitles}')
                    x = -1
                    while not (0 <= x <= len(wTitles)-1):
                        index = 0
                        xList = []
                        for wTitle in wTitles:
                            if wTitle not in xList:
                                xList.append(wTitle)
                                index += 1
                        if len(xList) > 1:
                            print(f'Please choose which window of {app} you want to '
                                'use with Pixel:')
                            y = -1
                            while not (0 <= y <= len(xList)-1):
                                for wTitle in xList:
                                    print(xList.index(wTitle), wTitle)
                                try:    
                                    y = int(input())
                                except ValueError:
                                    print('Please choose a number...\n')
                            windows = pywinctl.getWindowsWithTitle(title=xList[y])
                            if len(windows) == 1:
                                appWindow = windows[0]
                                return appWindow.getHandle()
                        # app has many windows with same name
                        windows = pywinctl.getWindowsWithTitle(title=wTitles[0])
                        _tryLogger_(log='The selected app has more than one window '
                                    f'with name: {windows[0].title}')
                        x = -1
                        while not (0 <= x <= len(windows)-1):
                            print(f'Please choose which window of {app} you want '
                                f'to use with Pixel from 0 to {len(windows)-1}')
                            try:    
                                x = int(input())
                            except ValueError:
                                print('Please choose a number...\n')
                        appWindow = windows[x]
                        return appWindow.getHandle()
        except Exception as e:
            _tryLogger_(log=f"Error choosing the application window: {e}")
            return None
        return None

    def winWatchDog(self, ghostWindow: CustomWindow, os:str) -> bool:
        redrawTimer = Timer(callback=ghostWindow.drawGhostWindow,
                            logger=thisLogger)
        wWDCallback_wrapper = lambda data: wWDCallback(_=data,
                                                       ghostWindow=ghostWindow,
                                                       redrawTimer=redrawTimer)
        isVisibleCB_wrapper = lambda visible: isVisibleCB(visible=visible,
                                                          ghostWindow=ghostWindow)
        isAliveCB_wrapper = lambda alive: isAliveCB(alive=alive,
                                                    ghostWindow=ghostWindow)
        try:
            self.watchdog.start(movedCB=wWDCallback_wrapper,
                                resizedCB=wWDCallback_wrapper,
                                isVisibleCB=isVisibleCB_wrapper,
                                isAliveCB=isAliveCB_wrapper)
            if os == 'Darwin':
                self.watchdog.setTryToFind(tryToFind=True)
            if self.wdOverrideInterval is not None:
                self.watchdog.updateInterval(interval=self.wdOverrideInterval)
            _tryLogger_(log='Window watchdog started', level='debug')
            return True
        except Exception as e:
            _tryLogger_(log=f'Error starting window watchdog: {e}', level='critical')
            return False

# Watchdog callbacks:
def wWDCallback(_, ghostWindow, redrawTimer) -> None:
    if redrawTimer.is_running:
        _tryLogger_(log='timer thread running', level='debug')
        redrawTimer.reset()
    else:
        _tryLogger_(log='timer thread NOT running', level='debug')
        ghostWindow.hide()
        redrawTimer.start()

def isAliveCB(alive, ghostWindow: CustomWindow) -> None:
    if not alive:
        print(f'chiudo finestra')
        # ghostWindow.destroy()
        ghostWindow.emit(segnale)

def isVisibleCB(visible, ghostWindow) -> None:
    if not visible:
        ghostWindow.hide()
    else:
        ghostWindow.show()

def _tryLogger_(log: str, level: Literal['debug', 'info', 'error',
                'critical'] = 'debug') -> None:
    try:
        log_method = getattr(thisLogger, level)
        log_method(log)
    except Exception as e:
        print(f'Error writing log: {e} '
                f'continuing with simple print\n{log}')
