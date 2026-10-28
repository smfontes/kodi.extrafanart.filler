import xbmc

class ShutdownException(Exception):
    pass

class ShutdownHandler:
    _monitor = xbmc.Monitor() 

    @staticmethod
    def raise_exception_on_abort():
        if ShutdownHandler._monitor.abortRequested():
            raise ShutdownException()
        