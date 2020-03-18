import random, threading
from timeit import default_timer as timer
import bluetooth
from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader

classID = random.random()
class Tooth(ruckusTUI.module):
    name = "Bluetooth Scanner"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))

        self.should_loop = False
        self.classID = classID

    def loop(self):
        while True:
            self.context['looping'] = "True"
            if not self.should_loop:
                break
            self.do_one_pass()
        self.context['looping'] = "False"

    def do_one_pass(self):
        start_scan = timer()
        scan = []
        for index, cell in enumerate(bluetooth.discover_devices()):
            scan.append({
                "index": index,
                "name": bluetooth.lookup_name( cell )
            })
        self.context['scantime'] = timer() - start_scan

    @ruckusTUI.callback(classID, ruckusTUI.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.should_loop:
            self.should_loop = False
        else:
            self.should_loop = True
            self.app.log.append("Starting bluetooth Scan")
            threading.Thread(target=self.loop).start()

    def page(self, panel=None):
        template = self.templates.get_template("tooth.j2")
        return template.render(context=self.context) 