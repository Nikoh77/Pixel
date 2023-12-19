import logging
import platform
from PySide6.QtCore import Signal
# import subprocess
# import sys
# from PySide6.QtWidgets import QApplication
# import pywinctl
# from PIL import Image, ImageGrab
import pytesseract # type: ignore
import deepl
from mymodules.ini import iniSettingsCheck, iniStructCheck, settings
from mymodules.ghost_window import CustomWindow, MyQtApp
# import cv2
# import inspect
# import threading
import colorlog
from mymodules.app_window import Window

"""
Defining root variables
"""
supportedOs: list[str] = ['Darwin', 'Windows', 'Linux']
os_name = platform.system()
configFile = 'config.ini'
settingsNeeded = {'transProvider': ['brand', 'api_key'], 'pixel': ['data1', 'data2']}
foldersNeeded: dict[str, str] = {'screenshots': 'img'}
logLevel = 'debug'
winWatchDogInterval: float | None = None
pixelWorkMode = 'selection'
timer: int = 1
logger = colorlog.getLogger(name=__name__)
ghostWindow: CustomWindow

def doLog():
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(levelname)-8s] %(blue)s %(asctime)s %(name)s %(reset)s %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'bold_red',
            'CRITICAL': 'bold_red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    currentLevel = logging.getLevelName(logger.getEffectiveLevel()).lower()
    if logLevel != ('' and None and currentLevel):
        getattr(logger, currentLevel)(f'switching from debug level {logging.getLevelName(logger.getEffectiveLevel())}')
        logger.setLevel(logLevel.upper())
        logger.debug(f'to level {logging.getLevelName(logger.getEffectiveLevel())}')

def doTranslate(text, transProvider_api_key=None):
    translator = deepl.Translator(auth_key=transProvider_api_key, send_platform_info=False)
    try:
        translation = translator.translate_text(text=text, target_lang="IT")
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
            logger.debug(msg=f'Assigning global variable {variable_name} from {configFile}')
            globals()[variable_name] = sub_value

def pixelMainLoop(app) -> None:
    appWindow = Window(wdOverrideInterval=winWatchDogInterval, logger=logger)
    if appWindow is None:
        logger.error(msg='Failed to start application')
        return
    ghostWindow = CustomWindow(appWindow=appWindow, screenShotsPath=foldersNeeded.get('screenshots'))
    if not appWindow.winWatchDog(ghostWindow=ghostWindow, os=os_name):
        logger.error(msg='Failed to start application')
        return
    logger.info(msg='Application started')
    app.exec()
    # app.exec(appWindow=appWindow)
    # screenshot = ImageGrab.grab(bbox=window.bbox)4

    # screenshot.save("screenshot.png")
    # screenshot=cv2.imread('hq720.png')
    # screenshot=cv2.cvtColor(screenshot, cv2.COLOR_RGBA2GRAY)

    # screenshot=cv2.threshold(screenshot, 220, 255, cv2.THRESH_BINARY)[1]
    # screenshot=cv2.medianBlur(screenshot,3)
    # cv2.imwrite('/home/nikoh/Scrivania/screenshot.jpg', screenshot)
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
    print('finito')

def doOCR(image, psm=None):
    try:
        if psm is not None:
            text = pytesseract.image_to_string(image=image, config=f'--psm {psm}')
        else:
            text = pytesseract.image_to_string(image=image)
        if text != (None or ''):
            logger.debug('Successfully recognized text...')
            return text
        else:
            return
    except FileNotFoundError:
        logger.error('Error finding OCR bin')
        return

def main() -> None:
    doLog()
    if not (iniSettingsCheck(options=settingsNeeded, config_file=configFile,
            logger=logger) and iniStructCheck(folders=foldersNeeded,
            logger=logger)):
        logger.critical(f'An error as occured initialising settings')
        return
    buildSettings(settings)
    if os_name not in supportedOs:
        logger.critical(f'{os_name} usupported OS')
        return
    logger.debug(msg=f'{os_name} OS detected')
    app = MyQtApp(logger=logger)
    pixelMainLoop(app=app)
    # sys.exit(app.exec())
    
if __name__ == '__main__':
    main()
    print('terminated')
