import asyncio
import os, sys, traceback, time
from timeit import default_timer as timer
from .demons import Demon
from .comms import Comms


class Backend(object):
    def __init__(self, app):
        self.app = app
        self.comms = Comms()
        # logic is only used in the frontend.
        self.logic = app.logic(self)
        self.running = True
        self.demon = Demon(self)

    def start(self): pass

    def stop(self): pass

    def show(self): pass

    def frontend_loop(self): pass

    def frontend_stop(self): pass

    def main_loop(self): pass


class TUISink(object):
    def __init__(self, app):
        self.app = app
        # modules
        self.frontend = app.frontend
        self.demon = Demon()
        # self.frontend.main_screen(self.app.name)
        self.logic = app.logic(self)
        self.CRASHED = False  # oh no!

        # runtime
        self.running = True

        # logging
        self.ERROR = lambda x: self.logger(x)  # registered D.B.A
        # this needs a timeout for the header.
        self.error_timeout = False

    def logger(self, message):
        """Logs messages to both the screen and to file.
        TODO: This needs more formatting, its worthwhile to spend the time here.!
        """
        # with open("logs/.log", 'a+') as f: f.write("\n"+f"[date] {str(message)}")
        filler = self.frontend.screen_w-7 - len(str(message))
        self.frontend.header[0].addstr(1, 1, f"ERR: {str(message)}"[:self.frontend.screen_w-3]+" "*filler)
        self.app.log.append(str(message))

    @property
    def is_running(self):
        return self.running

    def start(self):
        """This buffer is meant to transition to asyncio"""
        # self.loop.run_until_complete(self.main_loop())
        if self.app.splash_screen: self.frontend.spash_screen()
        self.frontend.main_screen(self.app.name)
        self.logic.setup_panels()
        self.main_loop()

    def main_loop(self):
        """This is the main loop. Framerate."""
        # self.logic.selector()
        try:
            while self.is_running:
                start_loop = timer()  # loop_timer.
                # time.sleep(.0075)   # <- wtf is this?? TODO::
                self.frontend.refresh() # update graphics
                keypress = 0   # have we grown out of this?
                keypress = self.frontend.get_input()
                if keypress: self.logic.decider(keypress)
                self.logic.all_page_update()  # this is a tick.
                loop_time = timer() - start_loop
                framerate = 30/1000
                if loop_time > framerate: pass
                else: time.sleep(framerate-loop_time)
                # TODO: self.frontend.fps(int(framerate*1000)) # this is now wrong... and not reporting actual framerate.
        except KeyboardInterrupt:
            pass
        except:
            # exc_type, exc_value, exc_traceback = sys.exc_info()
            formatted_lines = traceback.format_exc().splitlines()
            self.ERROR(" ".join(formatted_lines[-2:]))
            self.CRASHED = True
        finally:
            self.exit_program()
    
    def exit_program(self):
        self.frontend.end_safely()
        self.logic.end_safely()
        if self.CRASHED:
            os.system('clear')
            print("Captain! Something has gone wrong...")
            print("~"*60)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            # print("*** print_tb:")
            # print("*** tb_lineno:", exc_traceback.tb_lineno)
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            traceback.print_exc(file=sys.stdout)
            print(exc_type)
            print(exc_value)
            print("+"*60)
            

