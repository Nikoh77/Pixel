import logging
import os
import platform
import subprocess
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QBrush, QPainter, QPen
import pywinctl as pwc
from PIL import Image, ImageGrab
import pytesseract
import deepl
import ini_check
import time
import cv2
import inspect
import threading
import colorlog

def defGlobals(): # Defining root variables
    global_dict={'supportedOs':['Darwin','Windows','Linux'],
        'os_name':platform.system(),
        'user_name':os.getlogin(),
        'configFile':'config.ini',
        'configNeed':{'transProvider':['brand','api_key'],'pixel':['data1','data2']},
        'logLevel':'debug',
        'winWatchDogInterval':None,
        'pixelWorkMode':'selection',
        'timestamp':time.time()
        }
    for var, value in global_dict.items():
        globals()[var] = value
        logger.debug(f'Assigning global variable {var} from {inspect.currentframe().f_code.co_name}')

def doLog():
    formatter = colorlog.ColoredFormatter(
	"%(log_color)s[%(levelname)-8s] %(blue)s %(asctime)s %(name)s %(reset)s %(message)s",
	datefmt='%Y-%m-%d %H:%M:%S',
	reset=True,
	log_colors={
		'DEBUG':    'cyan',
		'INFO':     'green',
		'WARNING':  'yellow',
		'ERROR':    'bold_red',
		'CRITICAL': 'bold_red,bg_white',
	},
	secondary_log_colors={},
	style='%'
    )
    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)
    global logger
    logger = colorlog.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

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
                # if not(window.isActive):
                #     activated=window.activate(wait=True)
                #     if activated:
                #         logger.info(f'window {window.title} activated')
                #         try:
                #             window.alwaysOnTop(True)
                #         except Exception as e:
                #             logger.error(f'error when bringing {window.title} always on top')
                global appWindow
                appWindow=window
                logger.debug('Application window was chosen')
                return True
                    # else:
                    #     logger.error(f'error activating {window.title}')
                    #     return False
            else:
                logger.error('error1')
                return False
        else:
            logger.error('the selected app has more than one window')
            return False
    except Exception as e:
        logger.error(f"Error choosing the application window: {e}")
        return False

def isVisibleCB(visible):
    if not visible:
        qtWindow.hide()
    else:
        qtWindow.show()

def winWatchDog(interval=None):
    try:
        appWindow.watchdog.start(resizedCB=drawGhostWindow, movedCB=drawGhostWindow, isVisibleCB=isVisibleCB)
        if os_name=='Darwin':
            appWindow.watchdog.setTryToFind=True
        if interval!=None:
            appWindow.watchdog.updateInterval(interval)
        logger.debug('Window watchdog started')
        return True
    except Exception as e:
        logger.critical(f'Error starting window watchdog: {e}')
        return False

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

def drawGhostWindow(data=None): # data is mandatory to watchdog
    global timestamp
    if (round(time.time())-round(timestamp))<2:
        print('minore di 2 secondi')
        timestamp=time.time()
        return
    print('ok')
    timestamp=time.time()
    left, top, right, bottom = appWindow.bbox
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
    qtWindow.setGeometry(left,top,width,height)
    qtWindow.show()
    
def defineGhostWindow():
    global qtWindow
    qtWindow = customWindow()
    qtWindow.setAttribute(Qt.WA_NoSystemBackground, True)
    qtWindow.setAttribute(Qt.WA_TranslucentBackground, True)
    qtWindow.setWindowFlags(qtWindow.windowFlags() | Qt.FramelessWindowHint)
    global resolution
    size=app.primaryScreen().size().toTuple()
    resolution={'width':size[0],'height':size[1]}
    drawGhostWindow()
        
class customWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pixel ghost window')
    def paintEvent(self, event=None):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setOpacity(0.5)
        painter.setBrush(Qt.white)
        painter.setPen(QPen(Qt.white))   
        painter.drawRect(self.rect())

def pixelMainLoop():
    while True:
        # if not appWindow.watchdog.isAlive():
    # while tkRoot.winfo_exists():
            # print(appWindow.watchdog.isAlive())
            # break
        print('i am waiting...')
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
        time.sleep(10)
        tkRoot.quit()
        break

def doStart():
    if not ini_check.iniCheck(configNeed,configFile,logger):
        logger.critical(f'An error as occured initialising settings')
        return False
    buildSettings(ini_check.settings)
    if os_name not in supportedOs:
        logger.critical(f'{os_name} usupported OS')
        return False
    logger.debug(f'{os_name} OS detected')
    if not whichWindow():
        return False
    if not winWatchDog(winWatchDogInterval):
        return False
    global app
    app = QApplication()
    return True

def main():
    doLog()
    defGlobals()
    if logLevel!=('' and None):
        logger.info(f'switching from {logging.getLevelName(logger.level)} level to {logLevel.upper()}')
        logger.setLevel(logLevel.upper())
    if not doStart():
        logger.error('Failed to start application')
        return
    logger.info('Application started')
    # pixelThread = threading.Thread(target=pixelMainLoop)
    # pixelThread.start()
    defineGhostWindow()
    # logger.critical('Application terminated')
    # tkRoot.destroy()
    # return
    # sys.exit(app.exec())
    app.exec()
    
if __name__ == '__main__':
    main()
    print('terminated')