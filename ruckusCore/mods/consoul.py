import os, sys, socket, getpass, random, threading, subprocess
from .. import ruckusTUI
from jinja2 import Environment, FileSystemLoader

classID = random.random()
class Consoul(ruckusTUI.module):
    name = "Consoul"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        self.context['cwd'] = os.getcwd()
        self.context['username'] = getpass.getuser()
        self.context['hostname'] = socket.getfqdn()
        self.classID = classID
        self.process = False
        # self.setup()

    def setup(self):
        self.process = subprocess.Popen(
            ['/bin/bash'], 
            shell=False, 
            stdin=subprocess.PIPE, stdout=subprocess.PIPE
        )

    def page(self, panel=None):
        template = self.stock_templates.get_template("consoul.j2")
        render = template.render(context=self.context)
        #p = self.process.stdout.readline()   # <-- OH DUH this needs to be in a thread.
        #max_elements_to_display = self.frontend.winright_dims[0]-4
        #if p:
        #    panel.addstr(self.ind, 3, p)
        #    self.ind += 1
        #    if self.ind >= max_elements_to_display:
        #        self.ind = 3
        return render

    def string_decider(self, panel, string_input):
        # self.process.write(string_input)
        # self.context["text_input"] = string_input
        pass

    @ruckusTUI.callback(classID, ruckusTUI.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        pass