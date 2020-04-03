from .app import App
from .comms import Comms
from .utils import *
# from .__init__ import __version__
import os
import sys
from termcolor import colored, cprint
import subprocess

def command(command):
    proc = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE).stdout
    return proc.read().decode()

def help():
    help_list = [
        "| 'start' : summon the demon.",
        "| 'stop'  : protection from evil.",
        "| 'status': tell me what you know.",
        "| 'show'  : display the frontend.",
        "| 'version': display current version.",
        "| 'get'   : do a Tor CURL.",
        "| '??'    : NEXT THING."
    ]
    help_msg = str("\n".join(help_list))
    return help_msg

def get_request(data):
    url = data[1]
    if url:
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
    climsg = [
        colored('ruckusCore', 'magenta'),
        colored(f'V.{__version__}', 'blue'),
        colored(f'{get_user()}', 'green'),
        colored(f'{os.getcwd()}', 'cyan'),
        colored(f'\n$> ', 'red')
    ]
    cli_msg = colored(" | ", 'yellow').join(climsg)
    _ = data.pop(0)
    if data:
        command = data[0]

        if   command in ("get","--get"): 
            protected(get_request(data))

        elif command in ("version","--version"):
            print(f"RuckusCore version: {__version__}")

        elif command in ("na", "blank", "--whatever"):
            print("do stuff")

        elif command in ("na", "blank", "--whatever"):
            print("do stuff")

        else:
            print(f"RuckusCore Doesnt Support that yet. ==>\n\t{' '.join([*data])}")
    else:
        cprint(cli_msg)
        try:
            app = App()
            app.run()
        except:
            print("couldnt start app... something...")

if __name__ == "__main__":
    main()