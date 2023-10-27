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
import cv2
import inspect
import threading

def defGlobals(): # Defining root variables
    global_dict={'supportedOs':['Darwin','Windows','Linux'],
        'os_name':platform.system(),
        'user_name':os.getlogin(),
        'configFile':'config.ini',
        'configNeed':{'transProvider':['brand','api_key'],'pixel':['data1','data2']},
        'logLevel':'debug',
        'winWatchDogInterval':None,
        'pixelWorkMode':'selection'}
    for var, value in global_dict.items():
        globals()[var] = value
        logger.debug(f'Assigning global variable {var} from {inspect.currentframe().f_code.co_name}')
    
def doLog():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    global logger
    logger=logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

def doTranslate(text):
    translator=deepl.Translator(transProvider_api_key, send_platform_info=False)
    try:
        translation=translator.translate_text(text=text, target_lang="IT")
        return translation
    except deepl.exceptions.AuthorizationException:
        logger.error('DeepL API authorization failed')
    except Exception as e:
        logger.error(f'Error translating text: {e}')
    return

def buildSettings(data):
    for key, value in data.items():
        for sub_key, sub_value in value.items():
            variable_name = f'{key}_{sub_key}'
            variable_name = variable_name.replace(' ', '_')
            variable_name = variable_name.replace('-', '_')
            logger.debug(f'Assigning global variable {variable_name} from {configFile}')
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

def movedCB(pos):
    x=pos[0]
    y=pos[1]
    tkRoot.geometry(f'+{x}+{y}')

def resizedCB(edges):
    height=edges[0]
    length=edges[1]
    tkRoot.geometry(f'{height}x{length}')

def winWatchDog(window, interval):
    # movedCB=lambda pos: logger.info(f'moved: {window.bbox}')
    # resizedCB=lambda size: logger.info(f'resized: {window.bbox}')
    try:
        window.watchdog.start(resizedCB=resizedCB, movedCB=movedCB)
        if os_name=='Darwin':
            window.watchdog.setTryToFind=True
        if interval!=None:
            window.watchdog.updateInterval(interval)
        logger.debug('Window watchdog started')
        return window
    except Exception as e:
        logger.critical(f'Error starting window watchdog: {e}')
        return

def doOCR(image,psm=None):
    try:
        if psm != None:
            text=pytesseract.image_to_string(image=image, config=f'--psm {psm}')
        else:
            text=pytesseract.image_to_string(image=image)
        if text!=(None or ''):
            logger.debug('Successfully recognized text...')
            return text
        else:
            return
    except FileNotFoundError:
        logger.error('Error finding OCR bin')
        return

def ghostWindow():
    global tkRoot
    tkRoot = tk.Tk()
    tkRoot.title('Pixel')
    tkRoot.resizable(False, False)
    tkRoot.overrideredirect(True)
    tkRoot.wait_visibility(tkRoot)
    tkRoot.attributes('-alpha', 0.4)
    # left, top, right, bottom = window.bbox
    # width = right - left
    # height = bottom - top
    # tkRoot.geometry(f"{width}x{height}+{left}+{top}")
    tkRoot.mainloop()

def mainLoop(window):
    while window.watchdog.isAlive():
        print('ok')
        # screenshot = ImageGrab.grab(bbox=window.bbox)4
        
        # screenshot.save("screenshot.png")
        # screenshot=cv2.imread('hq720.png')
        # screenshot=cv2.cvtColor(screenshot, cv2.COLOR_RGBA2GRAY)
        
        # screenshot=cv2.threshold(screenshot, 220, 255, cv2.THRESH_BINARY)[1]
        # screenshot=cv2.medianBlur(screenshot,3)
        # cv2.imwrite('/home/nikoh/Scrivania/screeshot.jpg', screenshot)
        # contours, _=cv2.findContours(screenshot, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # screenshot_color = cv2.cvtColor(screenshot, cv2.COLOR_GRAY2BGR) 
        # cv2.drawContours(screenshot_color, contours, -1, (0,255,0), 2)
        # cv2.imshow('test image', screenshot_color)

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # toTranslate=doOCR(screenshot, 6)
        # print(toTranslate)
        # if toTranslate==None:
        #     logger.info('no text on this image')
        #     continue
        # translation=doTranslate(toTranslate)
        # if translation==None:
        #     logger.info('no translation for this text')
        # print(translation)
        time.sleep(5)
    return

def doStart():
    if not ini_check.iniCheck(configNeed,configFile,logger):
        logger.critical(f'An error as occured initialising settings')
        return False
    buildSettings(ini_check.settings)
    if os_name not in supportedOs:
        logger.critical(f'{os_name} usupported OS')
        return False
    logger.debug(f'{os_name} OS detected')
    window=whichWindow()
    if window==None:
        logger.error('no window selected')
        return False
    if winWatchDog(window,winWatchDogInterval):
        return window
    return False

def main():
    doLog()
    defGlobals()
    if logLevel!=('' and None):
        logger.info(f'switching from {logging.getLevelName(logger.level)} level to {logLevel.upper()}')
        logger.setLevel(logLevel.upper())
    startedWindow=doStart()
    if startedWindow==None:
        logger.error('Failed to start application')
        return
    logger.info('Application started')
    thread_gui = threading.Thread(target=ghostWindow)
    thread_gui.start()
    mainLoop(startedWindow)

    logger.critical('Application terminated')

    
if __name__ == '__main__':
    main()