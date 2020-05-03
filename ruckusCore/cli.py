import sys, inspect, os, asyncio
from timeit import default_timer as timer

# add to requirements.txt
from termcolor import colored, cprint
import zmq
from .utils import error_handler


class Command(object):
    def __init__(self):
        l1, l2 = (colored("[", "cyan"), colored("]", "cyan"))
        l3 = colored(">", "green")
        p1 = colored(f"ruckusc", "yellow")
        zero = colored("0", "blue")
        p2 = colored(f"re", "yellow")
        logo = f"{p1}{zero}{p2}"
        self.line = f"{l1}{logo}{l2}{l3}"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://ruckus.local:42069")
        data = sys.argv
        data.pop(0)
        if data:
            data = " ".join(data)
            if not sys.version_info >= (3, 7):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.single_pass(data))

            else:
                self.loop = asyncio.run(self.single_pass(data))
        else:
            if not sys.version_info >= (3, 7):
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.main_loop())
            else:
                self.loop = asyncio.run(self.main_loop())

    async def send(self, message): self.socket.send(bytes(message.encode("utf8")))

    async def recieve(self): return self.socket.recv().decode('utf8')

    async def single_pass(self, data):
        await self.send(str(data))
        message = await self.recieve()
        print(message)

    async def main_loop(self):
        while True:
            await asyncio.sleep(0.001)
            try:
                command = input(self.line)
                if command: 
                    await self.single_pass(command)
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
