import time, random
import threading
import RPi.GPIO as gpio
from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader

classID = random.random()
class GPIO(ruckusTUI.module):
    """My Raspi Control Module."""

    name = "RaspiGPIO"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)
        self.classID = classID
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        self.should_loop = False
        self.ind = 1
        self.content = []
        self.gpio_startup()
        self.setup()

    def setup(self):
        self.elements = ['POWER', "Startup Test", 'MOTOR1', 'MOTOR2', 'MOTOR3', 'MOTOR4']
        self.content = ["ON","",0,0,0,0]

    def gpio_startup(self):
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        gpio.setup(4, gpio.OUT)
        gpio.setup(18, gpio.OUT)
        # gpio.output(4, gpio.LOW)
        time.sleep(1)
        #gpio.output(4, gpio.HIGH)
        gpio.output(18, gpio.HIGH)
        # time.sleep(2)
        # gpio.output(4, gpio.LOW)
        
    def page(self, panel=None):
        ## Fix the scroller hack.                   #->
        if self.scroll < 0:                         #-> This should happen in the scroll button
            self.scroll = 0                         #-> but not all mods have the content vs 
        if self.scroll > len(self.elements):        #-> context b.s. going on. maybe it is the 
            self.scroll = len(self.elements)-1      #-> most sane way to do it. hard to say.
            ####################################    #->
        for index, element in enumerate(self.elements):
            color = self.frontend.palette[6]
            if index == self.scroll: color = self.frontend.color_rw
            panel.addstr(index+self.ind, 3, element, color)  # color bg white
            # l_index += 1 + len(element)
        # self.ind += len(self.elements)
        for index, element in enumerate(self.content):
            color = self.frontend.palette[7]
            if index == self.scroll: color = self.frontend.color_rw
            panel.addstr(index+self.ind, 13, str(element), color)  # color bg white
        
    def page_jinija(self, panel=None):
        template = self.templates.get_template("raspi.j2")
        return template.render(context=self.context)

    def blink(self, blinks=4):
        for x in range(blinks):
            gpio.output(19, gpio.HIGH)
            self.context = {
                "important data": "light on {} of {}".format(x+1, blinks)
            }
            time.sleep(1)
            gpio.output(19, gpio.LOW)
            self.context = {
                "important data": "light off           "
            }
            time.sleep(1)

    @ruckusTUI.callback(classID, ruckusTUI.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        cur_element = self.elements[self.scroll]
        if cur_element is "POWER":
            self.content[0] = "OFF" if self.content[0] is "ON" else "ON"
        if self.content[0] is "ON":
            self.game_engine.ERROR(f"power state going ON")
            gpio.output(4, gpio.LOW)
            gpio.output(18, gpio.LOW)
        else:
            self.game_engine.ERROR(f"power state going OFF")
            gpio.output(4, gpio.HIGH)
            gpio.output(18, gpio.HIGH)

    def end_safely(self):
        gpio.cleanup()
