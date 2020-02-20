import os, sys, pathlib

class Filesystem(dict):
    def __init__(self):
        self.user_home = pathlib.Path.home()
        self.user_conf = os.path.join(self.user_home, '.local')
        # make a .local folder for user
        if not os.path.exists(self.user_conf): os.mkdir(self.user_conf)
        # make a ruckusCore folder in .local
        self.app_dir = os.path.join(self.user_conf, 'ruckusCore')
        if not os.path.exists(self.app_dir): os.mkdir(self.app_dir)
        # make a pid file
        self.pid_file = os.path.join(self.app_dir, '.pidfile')
        if not os.path.exists(self.pid_file): 
            pathlib.Path(self.pid_file).touch()
            with open(self.pid_file, "w+") as f: f.write("0")
        # make a conf file
        self.conf_file = os.path.join(self.app_dir, 'conf.py')

    def __getattr__(self, attr): return self.get(attr)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__

    def __getstate__(self): return self

    def __setstate__(self, state):
        self.update(state)
        self.__dict__ = self