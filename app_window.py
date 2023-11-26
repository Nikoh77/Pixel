from typing import Callable, Optional, Literal
import pywinctl

class window(pywinctl.Window):
    """
    This class object is a custom pywinctl window implementation
    """
    def __init__(self, logger: Optional['logging.Logger'] = None):
        """
        Constructor of the class.
        
        Arguments:
            - logger (Optional[logging.Logger]): The logger instance from the `logging`
                module. Default is None.
        """
        self.logger = logger
        super().__init__(hWnd=self.whichWindow())

    def whichWindow(self):
        """
        In this function, active windows on the desktop are searched and listed for the
        user to choose which one Pixel should operate on.
        """
        try:
            apps=pywinctl.getAllAppsNames()
            self._tryLogger_(log=f'list of currently visible '
                                f'applications/windows: {apps}')
            x=-1
            while not(0 <= x <= len(apps)-1):
                print('Please choose which app you want to use with Pixel:')
                index=0
                for app in apps:
                    print(index, app)
                    index+=1
                try:    
                    x=int(input())
                except ValueError:
                    print('Please choose a number...\n')
            app=apps[x]
            self._tryLogger_(f'Application was chosen: {app}')
            wTitles=pywinctl.getAllAppsWindowsTitles().get(app)
            if len(wTitles)==1:
                # app has just one window
                wTitle=wTitles[0]
                appWindow = pywinctl.getWindowsWithTitle(wTitle)[0]
                return appWindow.getHandle()
            else:
                self._tryLogger_(f'the selected app has more than one window: '
                                f'{wTitles}')
                x = -1
                while not(0 <= x <= len(wTitles)-1):
                    index = 0
                    xList = []
                    for wTitle in wTitles:
                        if wTitle not in xList:
                            xList.append(wTitle)
                            index+=1
                    if len(xList)>1:
                        print(f'Please choose which window of {app} you want to '
                                'use with Pixel:')
                        y = -1
                        while not(0 <= y <= len(xList)-1):
                            for wTitle in xList:
                                print(xList.index(wTitle), wTitle)
                            try:    
                                y=int(input())
                            except ValueError:
                                print('Please choose a number...\n')
                        windows = pywinctl.getWindowsWithTitle(xList[y])
                        if len(windows) == 1:
                            appWindow = windows[0]
                            return appWindow.getHandle()
                    # app has many windows with same name
                    windows = pywinctl.getWindowsWithTitle(wTitles[0])
                    self._tryLogger_('The selected app has more than one window '
                                    f'with name: {windows[0].title}')
                    x = -1
                    while not(0 <= x <= len(windows)-1):
                        print(f'Please choose which window of {app} you want '
                                f'to use with Pixel from 0 to {len(windows)-1}')
                        try:    
                            x=int(input())
                        except ValueError:
                            print('Please choose a number...\n')
                    appWindow = windows[x]
                    return appWindow.getHandle()
        except Exception as e:
            self._tryLogger_(f"Error choosing the application window: {e}")
            return
        
    def _tryLogger_(self, log: str, level: Literal['debug', 'info', 'error'] = 'debug'):
        try:
            log_method = getattr(self.logger, level)
            log_method(log)
        except Exception as e:
            print(f'Error writing log: {e} '
                    f'continuing with simple print\n{log}')