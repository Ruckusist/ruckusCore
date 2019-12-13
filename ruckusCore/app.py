import ruckusCore
from ruckusCore import os

class App(object):
    """This is the App Factory"""

    name = "ruckusTUI"
    # global callbacks

    def __init__(self, modules=[]):
        self.modules = modules
        self.modules.append(ruckusCore.About)
        self._menu = []
        self.log = []
        self.splash_screen = True
        self.game_engine = None  # im caught in an import loop...
        self.frontend = ruckusCore.Window()
        self.logic = ruckusCore.Logic
        self.callbacks = ruckusCore.callbacks
        self.build()  # ==> THIS SHOULD BE UNCOMMENTED!!

    def build(self):
        """The Sink Module needs to be loaded after the modules are loaded."""
        # make file archive
        self.game_engine = ruckusCore.TUISink(self)
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

    """Key Press callback functions."""
    @ruckusCore.callback(ID=1, keypress=9)  # tab
    def on_tab(self, *args, **kwargs):
        self.game_engine.frontend.screen_mode = False
    @ruckusCore.callback(ID=1, keypress=113)  # q
    def on_q(self, *args, **kwargs):
        self.game_engine.running = False
    @ruckusCore.callback(ID=1, keypress=338)  # pg_down
    def on_pg_down(self, *args, **kwargs):
        if self.game_engine.logic.cur < len(self.menu)-1:
            self.game_engine.logic.cur += 1
        else:
            self.game_engine.logic.cur = 0
        self.game_engine.logic.selector()
    @ruckusCore.callback(ID=1, keypress=339)  # pg_up
    def on_pg_up(self, *args, **kwargs):
        if self.game_engine.logic.cur > 0:
            self.game_engine.logic.cur -= 1
        else:
            self.game_engine.logic.cur = len(self.menu)-1
        self.game_engine.logic.selector()