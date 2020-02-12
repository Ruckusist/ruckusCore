import os

class Demon(object):
    """
    The Demon should start ruckusCore in the background, and
    continue to manage tasks on the users behalf forever.

    this should provide functionality to the CLI. 
    start: start the demon.
    stop: stop the demon.
    status: current running state of demon and # of tasks.
    restart: reload the configs and restart the demon.

    it should also spin off an RPC server that can accept 
    all the rest of the CLI arguements to the running PID.
    """
    def __init__(self):
        self.pid = os.getpid()

def main():
    demon = Demon()
    print(demon.pid)



if __name__ == "__main__":
    main()