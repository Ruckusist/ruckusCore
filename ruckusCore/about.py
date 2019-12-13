import random
from .module import Module


aboutID = random.random()
class About(Module):
    name = "About"
    def __init__(self, app):
        super().__init__(app)
        self.classID = aboutID

    def page(self, panel=None):
        template = self.templates_stock.get_template("about.j2")
        return template.render(context=self.context)