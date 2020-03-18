import time, threading, random
from timeit import default_timer as timer
from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader
from MPUdriver import MPUDriver as mpu
#try:
#    import mpudriver
#except ImportError:
#    import mods.mpudriver as mpudriver

classID = random.random()
class MPU6050(ruckusTUI.module):
    """My Raspi Control Module."""

    name = "MPU 6050"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        self.should_loop = False
        self.classID = classID
        self.context['scantime'] = 0
        self.mpudriver = mpu()
        self.context["MPU"] = self.mpudriver.context
        self.mpudriver.setup()

    def loop(self):
        while True:
            if not self.should_loop: break
            self.context['looping'] = "True"
            start_action = timer()
            self.context["MPU"] = self.mpudriver()
            self.context['scantime'] = timer() - start_action
        self.context['looping'] = "False"
      
    @ruckusTUI.callback(classID, ruckusTUI.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.should_loop: self.should_loop = False
        else:
            self.should_loop = True
            # self.app.log.append("Starting MPU Scan")
            threading.Thread(target=self.loop).start()

    def end_safely(self):
        self.should_loop = False

    def page(self, panel=None):
        template = self.templates.get_template("mpu.j2")
        return template.render(context=self.context)
