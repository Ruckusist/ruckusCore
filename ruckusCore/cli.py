import sys, inspect, os, subprocess
import asyncio
from timeit import default_timer as timer
from .utils import error_handler
from termcolor import colored, cprint

# THIS SHOULD NOT BE MANUAL
# THIS CALLBACK SYSTEM SHOULD BE
# BUILD BY THE CONTRIBUTING CLASS
# THIS SHOULD JUST COMPILE THAT

from .filesystem import Filesystem
from .datasmith import Datasmith


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
  

class Command(object):
    def __init__(self):
        self.filesystem = Filesystem()
        self.datasmith = Datasmith()
        self.local_calls = {
            # GENERIC CALLS
            "help": self.help,

            # DATA SMITH CALLS
            "markets": self.datasmith.list_markets,
            "download": self.datasmith.get_historical_update,
            "graph": self.datasmith.ascii_graph
        }

        data = sys.argv
        data.pop(0)
        if data:
            self.loop = asyncio.run(self.parse_command(data))
        else:
            self.loop = asyncio.run(self.main_loop())

    async def help(self, *args):
        """Show the help message."""
        help_list = [
            "| 'start'    : summon the demon.",
            "| 'stop'     : protection from evil.",
            "| 'status'   : tell me what you know.",
            "| 'show'     : display the frontend.",
            "| 'version'  : display current version.",
            "| 'download' : refresh charts from coinbase.",
            "| 'help'     : Shows this screen.",
            "| '??'       : NEXT THING."
        ]
        help_msg = str("\n".join(help_list))
        print( help_msg )

    async def that(self, *args):
        """Test function."""
        print("this that")

    async def system_call(self, cmd):
        process = subprocess.Popen(
            " ".join(cmd), 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=os.getcwd(), 
            universal_newlines=True, 
            shell=True)
        output = process.communicate()
        stdout = output[0]
        return stdout

    async def parse_command(self, cmd):
        root = cmd[0]
        if root in tuple(list(self.local_calls)):
            return await self.local_calls[root](cmd)
        else:
            return await self.system_call(cmd)

    async def main_loop(self):
        while True:
            await asyncio.sleep(0.001)
            try:
                l1, l2 = (colored("[", "cyan"), colored("]", "cyan"))
                l3 = colored(">", "green")
                logo = colored("ruckusc0re", "yellow")
                line = f"{l1}{logo}{l2}{l3}"

                start_time = timer()
                command = None
                while timer() <= start_time + 5:
                    command = input(line)
                break



                if command:
                    result = await self.parse_command(command.split())
                    if result: print(result)
            except KeyboardInterrupt: print(); break
            except Exception:
                exception = sys.exc_info()
                outer_err = inspect.stack()[-1]
                offender = inspect.trace()[-1]
                error_handler(
                    exception, 
                    outer_err, 
                    offender
                )
                pass


def main(): Command()

if __name__ == "__main__":
    main()