from typing import Callable, Optional, Literal
import logging
import threading
import time


class Timer():
    """
    This class object is a simple timer implementation...
    """
    def __init__(self, seconds: int = 1, callback: Optional[Callable]
                 = None, logger: Optional['logging.Logger'] = None) -> None:
        """
        Constructor of the class.

        Arguments:
        - seconds (Optional[int]): The number of seconds. Default is None.
        - callback (Optional[Callable]): The callback function. Default is None.
        - logger (Optional[logging.Logger]): The logger instance from the `logging`
            module. Default is None.
        """
        self.seconds: int = seconds
        self.callback = callback
        self.logger = logger
        self.time_left: float = seconds
        self.timer_thread = None
        self.is_running = False

    def _timer_function(self):
        while self.time_left > 0 and self.is_running:
            self._tryLogger_(log='Timer started, cycle entered')
            time.sleep(0.5)
            self.time_left -= 0.5
        if self.is_running:
            self.is_running = False
            if self.callback is not None:
                self._tryLogger_(log="Timer completed!")
                self.callback(redraw=True)  # callback with bool to know between drawing and
                # redrawing after moved/resized
            else:
                self._tryLogger_("timer completed silently, no callback was "
                                 "given.")
                
    def start(self):
        """
        Start timer.
        """
        if not self.is_running:
            self.is_running = True
            self.time_left = self.seconds
            self.timer_thread = threading.Thread(target=self._timer_function)
            self.timer_thread.start()
        else:
            self._tryLogger_('Error starting timer, already running')

    def stop(self):
        """
        Stop timer.
        """
        if self.is_running:
            self.is_running = False
            self._tryLogger_('Timer reset')
        else:
            self._tryLogger_('Error stopping timer, isn\'t running')

    def reset(self):
        """
        Reset timer to original time left value.
        """
        if self.is_running:
            self.time_left = self.seconds
            self._tryLogger_('Timer reset')
        else:
            self._tryLogger_('Error resetting timer, isn\'t running')
            
    def _tryLogger_(self, log: str, level: Literal['debug', 'info', 'error'] = 
                    'debug'):
        try:
            log_method = getattr(self.logger, level)
            log_method(log)
        except Exception as e:
            print(f'Error writing log: {e} '
                  f'continuing with simple print\n{log}')
