import os, sys, asyncio, inspect, subprocess
import time
from timeit import default_timer as timer


## add to requirements.txt
import zmq
import setproctitle
from termcolor import colored, cprint

# local files
from .filesystem import Filesystem
from .datasmith import Datasmith
from .utils import error_handler, protected
from .demons import Demon
from .logo import *

class Server(object):
    def __init__(self):
        # ruckuscore
        self.filesystem = Filesystem()
        self.datasmith = Datasmith()
        self.demons = Demon()

        # zmq server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://10.42.0.1:42069")
        setproctitle.setproctitle("ruckuscore demon")
        self.running = True

        self.local_calls = {
            # GENERIC CALLS
            "help": self.help,

            # DATA SMITH CALLS
            "pair": self.datasmith.full_status,
            "markets": self.datasmith.list_markets,
            "download": self.datasmith.get_historical_update,
            "graph": self.datasmith.ascii_graph,
            "purge": self.datasmith.purge_files,
            "tops": self.datasmith.tops,
            "system": self.system_call
        }

        self.setup()
        print("RuckusC0re Server is Running.")

    def setup(self):
        # TODO: IMPLEMENT LOG ROTATING.
        self.log_path = os.path.join(self.filesystem.app_dir, "logs")
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        # if log_file.size is huge : rotate log
        self.log_file = os.path.join(self.log_path, "log.txt")

    def end_safely(self):
        # how to end  zmq
        self.log_file.close()

    @protected
    def start(self):
        asyncio.run(self.main_loop())

    async def send(self, message):
        if message:
            if type(message) == list:
                message = "\n".join(message)
            await self.log(f"--> {message}")
            self.socket.send(bytes(message.encode("utf8")))

    async def recieve(self): 
        message = self.socket.recv().decode('utf8')
        print(message)
        await self.log(f"<-- {message}")
        return message

    async def log(self, message, file=None):
        if not file: file = self.log_file
        if message:
            timez = colored(f"[{int(time.time())}]", "cyan")
            message = timez + message
            # print(message)
            with open(file, "a+") as f:
                print(message, file=f)

    async def help(self, *args):
        """Show this help message."""
        messages = []
        for k, v in self.local_calls.items():
            messages.append(f"{colored(k, 'green'):10s}: {colored(v.__doc__, 'red')}")
        messages.append(f"{colored('Visit: https://Ruckusist.com for more help', 'blue')}")
        return messages

    @protected
    async def system_call(self, *args):
        """Run a system command on the server"""
        args = args[0].split()
        print("system call: " + " ".join(args[1:]))
        process = subprocess.Popen(
            " ".join(args[1:]), 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            cwd=os.getcwd(), 
            universal_newlines=True, 
            shell=True)
        output = process.communicate()
        stdout = output[0]
        return str(stdout)

    @protected
    async def parse_command(self, cmd):
        root = cmd.split()[0]
        if root in tuple(list(self.local_calls)):
            return await self.local_calls[root](cmd)
        else:
            message = colored(f"[CMD] Not Found: ", "red") + cmd
            return message

    async def main_loop(self):
        while self.running:
            message = await self.recieve()
            if message:
                if message == "quit":
                    await self.send("Server shutting down.")
                    break
                else:
                    result = await self.parse_command(message)
                    await self.send(result)


def main():
    server = Server()
    server.start()


if __name__ == "__main__":
    main()