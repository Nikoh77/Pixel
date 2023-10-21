import logging
import os
import platform
import tkinter as tk
import pywinctl as pwc
from PIL import ImageGrab

# Defining root variables
supportedOs=['Darwin','Windows','Linux']
os_name=platform.system()
user_name = os.getlogin()

# Start logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
#logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def doStart():
    try:
        apps=pwc.getAllAppsNames()
        logger.info(f'list of currently open applications/windows: {apps}')
        _app=8
        while not(0 <= _app <= len(apps)+1):
            print('Please choose which app you want to use pixel with:')
            for app in apps:
                print(apps.index(app), app)
            try:    
                _app=int(input())
            except ValueError:
                print('Please choose a number...\n')
        app=apps[_app]
        windows=pwc.getAllAppsWindowsTitles().get(app)
        print(windows)
        if len(windows)==1:
            window=pwc.getWindowsWithTitle(windows[0])
        else:
            pass
        print(type(window[0]))
        # window=windows[]
        # print(windows[0].getClientFrame())
        # windows[0].activate(True)
        # # root = tk.Tk()
        # # root.title("Pixel")
        # # root.mainloop()
        # screenshot = ImageGrab.grab(bbox=(1233, 317, 2513, 1250))
        # screenshot.save("screenshot.png")
    except Exception as e:
        logger.error(f"Error: {e}")

        
def main():
    if os_name in supportedOs:
        doStart()
    else:
        logger.info('unsupported platform/OS')
        return
    
if __name__ == '__main__':
    main()