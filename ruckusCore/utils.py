import time, os
import datetime as dt
import sys, functools
import threading, inspect
import socket
import getpass
from termcolor import colored, cprint

def get_user(): return colored(f"{getpass.getuser()}@{socket.gethostname()}", "cyan")

def get_time(): return colored(time.strftime("%b %d, %Y|%I:%M%p", time.localtime()), "yellow")

def error_handler(exception, outer_err, offender, logfile="", verbose=True):
    try:
        outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
        off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
        error_msg = []
        error_msg.append(f"╔══| Errors® |═[{get_time()}]═[{get_user()}]═[{colored(os.getcwd(), 'green')}]═══>>")
        error_msg.append(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}")
        error_msg.append(f"║ \t{outer_err[2]}: {outer_off}  -->")
        error_msg.append(f"║ ++ {offender[1]} :: Func: {offender[3]}()")
        error_msg.append(f"║ -->\t{offender[2]}: {off}")
        error_msg.append(f"║ [ERR] {exception[0]}: {exception[1]}")
        error_msg.append(f"╚══════════════════════════>>")
        msg = "\n".join(error_msg)
        # print(msg)
        return msg
    except: print("There has been Immeasureable damage. Good day.")

def protected(func, logfile="", verbose=True):
    """Allows a function to die without killing the app."""
    @functools.wraps(func)
    def p_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            # this is a bad fix... i dont know WTF
            # its been too long since i worked in this
            # area. TODO the Exception should catch
            # all the errors including keyboard, but
            # doesnt. grrrrrrrr.
            print("Keyboard Interrupt: Ending Safely.")
            pass
        except Exception:
            exception = sys.exc_info()
            outer_err = inspect.stack()[-1]
            offender = inspect.trace()[-1]
            err = error_handler(
                exception, 
                outer_err, 
                offender, 
                logfile, 
                verbose
            )
            print(err)
    return p_func

def is_prime(n):
    """Picked up this func doing pushups on hackerrank."""
    if n <= 3:
        if n > 1: return True
        else: return False
    else:
        if n % 2 == 0 or n % 3 == 0: return False
    for i in range(5, floor(sqrt(n))):
        if n % i == 0 or n % i + 2 == 0: return False
    return True

def isnotebook():
    # https://stackoverflow.com/questions/15411967
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter


class Timer:
    # https://github.com/jaungiers/LSTM-Neural-Network-for-Time-Series-Prediction/blob/master/core/utils.py
    def __init__(self):
        self.start_dt = dt.datetime.now()

    def start(self):
        self.start_dt = dt.datetime.now()

    def stop(self):
        end_dt = dt.datetime.now()
        return f"Time taken: {end_dt - self.start_dt}"

#######################################################
#  TESTS
#######################################################

@protected
def test(this=1, that="this", options={"those":2}):
    list_ = [this]
    for i in range(2):
        print(f"[test()] {list_[i]}")

def test2(this=1, that="this", options={"those":2}):
    list_ = [this]
    for i in range(2):
        print(f"[test()] {list_[i]}")

if __name__ == "__main__":
    t = Timer()
    test(8)
    p_test = protected(test2)
    p_test(this=2)
    print("Program Still Running!")
    print(f"@protected: {protected.__doc__}")
    print(t.stop())