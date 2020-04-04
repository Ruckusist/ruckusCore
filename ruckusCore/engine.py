import asyncio, random
import os, sys, traceback, time, inspect
from timeit import default_timer as timer
from .demons import Demon
from .comms import Comms
from .utils import error_handler


class Backend(object):
    def __init__(self, app):
        self.app = app
        self.comms = Comms()
        # logic is only used in the frontend.
        self.logic = app.logic(self)
        self.running = True
        self.demon = Demon(self)

        # runtime
        self.runtime = timer()
        self.running = True
        self.CRASHED = False

        self.show_frontend = False

        # logging
        self.ERROR = lambda x: self.logger(x, "ERROR")

    def logger(self, message, message_type):
        """this should be done in the utils with the other error logging."""
        #  TODO
        print(f"[{message_type}] {message}")

    def start(self):
        try:
            print("Starting main loop.")
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            # so it should never end this way.
            print("Keyboard Interrupt: Ending Safely.")
        except Exception:
            exception = sys.exc_info()
            outer_err = inspect.stack()[-1]
            offender = inspect.trace()[-1]
            error_handler(
                exception, 
                outer_err, 
                offender
            )
        finally:
            self.exit_program()
        

    def stop(self): pass

    def show(self): pass

    async def frontend_loop(self): pass

    def frontend_stop(self): pass

    async def main_loop(self):
        while self.running:
            await asyncio.sleep(1.5)
            try:
                print("this is running.")
                if random.random() > .5:
                    print("random things happening")
                    x = list(x for x in range(5))
                    for i in range(6):
                        y = x[i]
            except Exception:
                exception = sys.exc_info()
                outer_err = inspect.stack()[-1]
                offender = inspect.trace()[-1]
                error_handler(
                    exception, 
                    outer_err, 
                    offender
                )

    def exit_program(self):
        self.logic.end_safely()
        print("this is the last message.")


class TUISink(object):
    def __init__(self, app):
        self.app = app
        # modules
        self.frontend = app.frontend
        self.demon = Demon(self)
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
        print("got this far.!")
        time.sleep(2)
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
