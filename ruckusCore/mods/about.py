import random
from ..module import Module
from ..callback import callback

aboutID = random.random()
class About(Module):
    name = "About"
    def __init__(self, app):
        self.classID = aboutID
        super().__init__(app)
        

    def page(self, panel=None):
        template = self.templates_stock.get_template("about.j2")
        return template.render(context=self.context)

    @callback(ID=aboutID, keypress=10)
    def on_enter(self, *args, **kwargs):
        self.visible = False