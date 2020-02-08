import ruckusCore
import random

classIDEx1 = random.random()
class Ex1(ruckusCore.Module):
    name = "Example 1"
    def __init__(self, app):
        super().__init__(app)
        self.classID = classIDEx1

    def page(self, panel):
        panel.addstr(1,1,"Example One.")
        return False

if __name__ == "__main__":
    app = ruckusCore.App([Ex1])
    try:
        ruckusCore.protected(app.run())
    finally:
        app.game_engine.exit_program()