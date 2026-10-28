import xbmc
from resources.lib.constants import Sender

def main():
    xbmc.executebuiltin(f"NotifyAll({Sender.CONTEXT_MENU_SENDER},{Sender.CONTEXT_MENU_OPERATION})")

if __name__ == "__main__":
    main()
