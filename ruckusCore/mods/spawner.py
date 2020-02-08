import threading
from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader


class Main(ruckusTUI.module):
    name = "Test"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)

    def page(self, panel=None):
        template = self.templates.get_template("spawn.j2")
        return template.render(context=self.context)


class Spawn(object):
    def __init__(self, app):
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        pass

    def page(self, panel=None):
        template = self.templates.get_template("spawn.j2")
        return template.render(context=self.context)
