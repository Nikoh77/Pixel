import logging
import os
import platform
import tkinter
import pywinctl as pwc

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
        windows=pwc.getAllAppsNames()
        logger.info(f'list of currently open applications: {windows}')
        root = tkinter.Tk()
        root.title("Pixel")
        root.mainloop()
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