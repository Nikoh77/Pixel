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



def extract_rect(rect_string):
    rect_string = rect_string.replace("Rect", "").replace("(", "").replace(")", "")
    values = rect_string.split(',')
    left_value = int(values[0].split('=')[1])
    top_value = int(values[1].split('=')[1])
    right_value = int(values[2].split('=')[1])
    bottom_value = int(values[3].split('=')[1])
    return left_value, top_value, right_value, bottom_value

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
        wTitles=pwc.getAllAppsWindowsTitles().get(app)
        if len(wTitles)==1:
            title=wTitles[0]
            windows=pwc.getWindowsWithTitle(title)
            if len(windows)==1:
                window=windows[0]
                if not(window.isActive):
                    activated=window.activate(wait=True)
                    if activated:
                        try:
                            window.alwaysOnTop(True)
                        except Exception as e:
                            logger.error(f'error when bringing {window} always on top')
                    else:
                        logger.error(f'error activating {window}')
                        
            else:
                pass
        else:
            pass
        rect_string=str(window.getClientFrame())
        data=extract_rect(rect_string)
        # # root = tk.Tk()
        # # root.title("Pixel")
        # # root.mainloop()
        screenshot = ImageGrab.grab(bbox=data)
        screenshot.save("screenshot.png")
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