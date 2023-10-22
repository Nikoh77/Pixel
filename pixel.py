import logging
import os
import platform
import tkinter as tk
import pywinctl as pwc
from PIL import Image, ImageGrab
import pytesseract
import deepl
import ini_check

# Defining root variables
supportedOs=['Darwin','Windows','Linux']
os_name=platform.system()
user_name = os.getlogin()
configFile='config.ini'
configNeed = {'DeepL':['api_key'],'TEST':['api_key','group_key']}

# Start logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
#logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def doTranslate(data):
    translator = deepl.Translator(DeepLapi_key)
    try:
        result = translator.translate_text("Hello, world!", target_lang="IT")
        print(result.text)
    except deepl.exceptions.AuthorizationException:
        logger.error('DeepL API authorization failed')


def extractImageRect(rect_string):
    rect_string = rect_string.replace("Rect", "").replace("(", "").replace(")", "")
    values = rect_string.split(',')
    left_value = int(values[0].split('=')[1])
    top_value = int(values[1].split('=')[1])
    right_value = int(values[2].split('=')[1])
    bottom_value = int(values[3].split('=')[1])
    return left_value, top_value, right_value, bottom_value

def buildSettings(data):
    for key, value in data.items():
        variable_name = key
        for sub_key, sub_value in value.items():
            variable_name += sub_key
            variable_name = variable_name.replace(' ', '_')
            variable_name = variable_name.replace('-', '_')
            globals()[variable_name] = sub_value

def whichWindow():
    try:
        apps=pwc.getAllAppsNames()
        logger.info(f'list of currently open applications/windows: {apps}')
        myApp=-1
        while not(0 <= myApp <= len(apps)+1):
            print('Please choose which app you want to use with Pixel:')
            for app in apps:
                print(apps.index(app), app)
            try:    
                myApp=int(input())
            except ValueError:
                print('Please choose a number...\n')
        app=apps[myApp]
        wTitles=pwc.getAllAppsWindowsTitles().get(app)
        if len(wTitles)==1:
            title=wTitles[0]
            windows=pwc.getWindowsWithTitle(title)
            if len(windows)==1:
                window=windows[0]
                if not(window.isActive):
                    activated=window.activate(wait=True)
                    if activated:
                        rectString=str(window.getClientFrame())
                        try:
                            window.alwaysOnTop(True)
                        except Exception as e:
                            logger.error(f'error when bringing {window} always on top')
                        return rectString
                    else:
                        logger.error(f'error activating {window}')
            else:
                pass
        else:
            pass
    except Exception as e:
        logger.error(f"Error: {e}")

def doStart():
    iniResult=ini_check.iniCheck(configNeed,configFile)
    if iniResult:
        buildSettings(ini_check.settings)
        rectString=whichWindow()
        data=extractImageRect(rectString)
        # root = tk.Tk()
        # root.title("Pixel")
        # root.mainloop()
        screenshot = ImageGrab.grab(bbox=data)
        # screenshot.save("screenshot.png")
        toTranslate=pytesseract.image_to_string(image=screenshot, lang='ita')
        doTranslate(toTranslate)

def main():
    if os_name in supportedOs:
        doStart()
    else:
        logger.info('unsupported platform/OS')
        return
    
if __name__ == '__main__':
    main()