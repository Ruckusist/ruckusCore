from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader
from ruckusTUI.mods import (
    # gpio_module, 
    fire,
    # tube,
    # wifi, 
    # mpu,
    consoul,
    # tooth,
)

class FunApp(ruckusTUI.app):
    """My Industy Breaking App."""

    name = "Working Examples"

    def __init__(self):
        # you need to start with the variables from the parent init.
        super().__init__()
        # self.splash_screen = True  # !!!
        # modules to load.
        # self.modules = [A list of AwesomeModules] will blow out the stock ones.
        # self.modules.append(gpio_module.GPIO)
        self.modules.append(fire.Fire)
        # self.modules.append(tube.Tube)
        # self.modules.append(wifi.Wifi)
        self.modules.append(consoul.Consoul)
        # self.modules.append(mpu.MPU6050)
        # self.modules.append(tooth.Tooth)
        # self.modules = [SweetModule]

        # this will build menu pages with the provided templates at startup.
        self.build()

    @ruckusTUI.callback(1, keypress=27)  # id=1 == class 1 is global, esc
    def fun_callback(self, *args, **kwargs):
        """Save the cheerleader, save the world."""
        self.game_engine.ERROR("this is just a test! no worries.")

    # @ruckusTUI.callback(1, keypress=27)
    @ruckusTUI.protected
    def DOOMED_function(self, *args, **kwargs):
        """This is so close to working..."""
        important_stuff = ['this', 'that']
        for i in range(3):
            self.game_engine.ERROR(important_stuff[i])
        self.game_engine.ERROR("DOOM!")


if __name__ == "__main__":
    app = FunApp()
    app.run()
