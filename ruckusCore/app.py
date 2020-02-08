"""  This is not gonna work anymore...
import ruckusCore
from ruckusCore import os
import pathlib
"""
import os, pathlib
from .mods.about import About
from .frontend import Window
from .logic import Logic
from .engine import TUISink
from .callback import callback, callbacks
from .utils import protected, get_time, get_user
from .comms import Comms
# import ruckusCore

class App(object):
    """This is the App Factory"""

    name = "ruckusCore"
    # global callbacks

    def __init__(self, modules=[]):
        self.modules = modules
        self.modules.append(About)
        self._menu = []
        self.log = []
        self.protected = protected
        self.splash_screen = False
        self.game_engine = None  # im caught in an import loop...
        self.frontend = Window()
        self.comms = Comms()
        self.get_request = self.get = lambda x: self.comms(x)
        self.logic = Logic
        self.callbacks = callbacks
        self.make_paths()
        self.build()


    def make_paths(self):
        # generate paths if they dont exist.
        # first will be "user/.local"
        pt = os.path.join(pathlib.Path.home(), '.local')
        if not os.path.exists(pt): os.makedirs(pt)

        # then its ".local/ruckusCore"
        self.app_path = self.appPath = os.path.join(pt, "ruckusCore")
        if not os.path.exists(pt): os.makedirs(pt)

    def build(self):
        """The Sink Module needs to be loaded after the modules are loaded."""
        # make file archive
        self.game_engine = TUISink(self)
        if self.modules:
            for mod in self.modules:
                mod(self)

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, mlist):
        self._menu = mlist

    def run(self):
        """Entry to the main loop."""
        self.game_engine.start()
        # self.log.append("Started App.")  # DEPRICATED !!

    def header(self, msg=None):
        # set the header message
        if not msg:
            msg = f"  {self.name}({get_user()})|{get_time()}" # {get_ip()} <-- not a thing.
        return msg

    """Key Press callback functions."""
    @callback(ID=1, keypress=9)  # tab
    def on_tab(self, *args, **kwargs):
        self.frontend.screen_mode = False
    @callback(ID=1, keypress=113)  # q
    def on_q(self, *args, **kwargs):
        self.game_engine.running = False
    @callback(ID=1, keypress=338)  # pg_down
    def on_pg_down(self, *args, **kwargs):
        if self.game_engine.logic.cur < len(self.menu)-1:
            self.game_engine.logic.cur += 1
        else:
            self.game_engine.logic.cur = 0
        self.game_engine.logic.selector()
    @callback(ID=1, keypress=339)  # pg_up
    def on_pg_up(self, *args, **kwargs):
        if self.game_engine.logic.cur > 0:
            self.game_engine.logic.cur -= 1
        else:
            self.game_engine.logic.cur = len(self.menu)-1
        self.game_engine.logic.selector()