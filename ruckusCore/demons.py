import os, sys  # noqa: E401
import psutil
from .filesystem import Filesystem

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


    def __init__(self, engine=None):
        self.filesystem = Filesystem()
        self.pid = os.getpid()
        self.pid_file = self.filesystem.pid_file
        self.dataset = {
            'is_app_running': True,
            'current_pid': 0,
            'running_app_pid': 0,
            'app_id_status': 0,
        }

    def start(self):
        """Fork--> Decouple--> Fork."""
        if psutil.WINDOWS:
            print("Cant Fork in windows. check.")
            return False

        def Fork():
            try:
                pid = os.fork()
                if pid > 0:
                    sys.exit(0)  # exit first parent.
                    os.setsid()
            except OSError as e:
                sys.stderr.write(
                    "fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            return pid

        pid = Fork()  # Fork 1
        # DECOUPLE
        os.chdir("/")
        os.umask(0)
        pid = Fork()  # Fork 2

    def stop(self, pid=None):
        if not pid: pid = self.pid  # noqa: E701
        process = self.inspect()
        process.terminate()

    def status(self, pid=None):
        if not pid: pid = self.pid  # noqa: E701
        process = psutil.Process(pid)
        return self.dataset

    def restart(self):
        # I dont have any idea how to do this.
        pass

    def inspect(self, pid=None):
        if not pid: pid = self.pid  # noqa: E701
        p = psutil.Process(pid)
        with p.oneshot():
            # execute internal routine once collecting multiple info
            self.dataset = {
                "name": p.name(),
                "cpu_times": p.cpu_times(),      # return cached value
                "cpu_percent": p.cpu_percent(),  # return cached value
                "create_time": p.create_time(),  # return cached value
                "ppid": p.ppid(),                # return cached value
                "status": p.status()             # return cached value
            }
        return p


def main():
    demon = Demon()
    print(demon.pid)


if __name__ == "__main__":
    main()