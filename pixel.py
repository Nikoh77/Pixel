import logging
import os
import platform
import tkinter as tk
import pywinctl as pwc
from PIL import Image, ImageGrab
import pytesseract
import deepl
import ini_check
import time

# Defining root variables
supportedOs=['Darwin','Windows','Linux']
os_name=platform.system()
user_name = os.getlogin()
configFile='config.ini'
configNeed = {'transProvider':['brand','api_key'],'pixel':['data1','data2']}
logLevel='debug'
winWatchDogInterval=None

def doLog():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    global logger
    logger=logging.getLogger(__name__)
    # logging.getLogger('deepl').setLevel(logging.DEBUG)
    # logging.getLogger('__main__').setLevel(logging.DEBUG)
    if logLevel == 'debug':
        return logging.DEBUG
    if logLevel == 'info':
        return logging.INFO
    elif logLevel == 'warning':
        return logging.WARNING
    elif logLevel == 'error':
        return logging.ERROR
    elif logLevel == 'critical':
        return logging.CRITICAL
    else:
        return logging.INFO  # default level

def doTranslate(data):
    print(transProvider_api_key)
    translator = deepl.Translator(transProvider_api_key, send_platform_info=False)
    try:
        result = translator.translate_text("Hello, world!", target_lang="IT")
        print(result.text)
    except deepl.exceptions.AuthorizationException:
        logger.error('DeepL API authorization failed')

def buildSettings(data):
    for key, value in data.items():
        for sub_key, sub_value in value.items():
            variable_name = f'{key}_{sub_key}'
            variable_name = variable_name.replace(' ', '_')
            variable_name = variable_name.replace('-', '_')
            logger.debug(f'Assigning global variable {variable_name}...')
            globals()[variable_name] = sub_value

def whichWindow():
    try:
        apps=pwc.getAllAppsNames()
        logger.debug(f'list of currently open applications/windows: {apps}')
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
                        logger.info(f'window {window.title} activated')
                        try:
                            window.alwaysOnTop(True)
                        except Exception as e:
                            logger.error(f'error when bringing {window.title} always on top')
                        return window
                    else:
                        logger.error(f'error activating {window.title}')
                        return
            else:
                logger.error('error1')
                return
        else:
            logger.error('error2')
            return
    except Exception as e:
        logger.error(f"Error: {e}")

def activeCB(active):
    print("NEW ACTIVE STATUS", active)

def movedCB(pos):
    print("NEW POS", pos)

def winWatchDog(window, interval):
    movedTestCB=lambda pos: print(window.bbox)
    try:
        window.watchdog.start(isActiveCB=activeCB, movedCB=movedTestCB)
        if os_name=='Darwin':
            window.watchdog.setTryToFind=True
        if interval!=None:
            window.watchdog.updateInterval(interval)
        logger.debug('Window watchdog started')
        return window
    except Exception as e:
        logger.critical(f'Error starting window watchdog: {e}')
        return
    
def doStart():
    if not ini_check.iniCheck(configNeed,configFile):
        return False
    buildSettings(ini_check.settings)
    if os_name not in supportedOs:
        logger.critical(f'{os_name} usupported OS')
        return False
    logger.debug(f'{os_name} OS detected')
    window=whichWindow()
    if window==None:
        print('nessuna finestra')
        return False
    if winWatchDog(window,winWatchDogInterval):
        return window
    return False

    # root = tk.Tk()
    # root.title("Pixel")
    # root.mainloop()
    # toTranslate=pytesseract.image_to_string(image=screenshot, lang='ita')
    # doTranslate(toTranslate)

def mainLoop(window):
    while window.watchdog.isAlive():
        screenshot = ImageGrab.grab(bbox=window.bbox)
        screenshot.save("screenshot.png")
        toTranslate=pytesseract.image_to_string(image=screenshot, lang='ita')
        print(toTranslate)
        time.sleep(5)
    return

def main():
    logging.getLogger().setLevel(doLog())
    startedWindow=doStart()
    if startedWindow!=None:
        logger.info('Application started')
        mainLoop(startedWindow)
    else:
        logger.info('Failed to start application')
        return
    logger.info('Application terminated')
    
if __name__ == '__main__':
    main()