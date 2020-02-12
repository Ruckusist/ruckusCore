try:
    from .comms import Comms
except ImportError:
    from comms import Comms
try:
    from .utils import protected
except ImportError:
    from utils import protected
import os
import sys

def get_request(data):
    if data:
        url = data.pop(0)
        com = Comms()
        com = protected(com)  # ?? not working.
        try:
            request = com(str(url))
            if request:
                print(request.text)
        except Exception as e:
            print(e)
    else:
        print("ruckuscore:get ==> requires 1 para: URL")

def main():
    """Main Entry Point for ruckusCore CLi"""
    data = sys.argv
    filename = data.pop(0)
    if data:
        command = data.pop(0)

        if   command in ("get","--get"): 
            get_request(data)

        elif command in ("version","--version"):
            print(f"RuckusCore version: {ruckusCore.__version__}")

        else:
            print(f"RuckusCore Doesnt Support that yet. ==>\n\t{', '.join([command, *data])}")

if __name__ == "__main__":
    main()