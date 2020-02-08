## this would be a cool thing.

import functools, random
try:
    import engine
except ImportError:
    from ruckusTUI import engine
from jinja2 import Environment, FileSystemLoader


glancesID = random.random
class glances(ruckusTUI.module):
    name = glances
    def __init__(self, app):
        super().__init__(app)
        self.classID = glancesID
        self.content = []
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        self.setup()

    def setup(self):
        self.elements.append("nada")

    def page(self, panel=None):
        template = self.templates_stock.get_template("glances.j2")
        return template.render(context=self.context)

    def end_safely(self): return

    @callback(glancesID, ruckusTUI.Key.ENTER)
    def on_enter(self, *args, **kwargs): return
