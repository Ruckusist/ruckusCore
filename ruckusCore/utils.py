import time, os
import sys, functools
import threading, inspect
import socket
import getpass


def get_user(): return f"{getpass.getuser()}@{socket.gethostname()}"

def get_time(): return time.strftime('%b %d, %Y %l:%M%p')

def error_handler(exception, outer_err, offender, logfile="", verbose=True):
    outer_off = ''.join([x.strip(' ').strip('\n') for x in outer_err[4]])
    off = ''.join([x.strip(' ').strip('\n') for x in offender[4]])
    print(f"╔══| Errors® |═[{get_time()}]═[{get_user()}]═[{os.getcwd()}]═══>>")
    print(f"║ {outer_err[1]} :: {'__main__' if outer_err[3] == '<module>' else outer_err[3]}")
    print(f"║ \t{outer_err[2]}: {outer_off}  -->")
    print(f"║ ++ {offender[1]} :: Func: {offender[3]}()")
    print(f"║ -->\t{offender[2]}: {off}")
    print(f"║ [ERR] {exception[0]}: {exception[1]}")
    print(f"╚══════════════════════════>>")

def protected(func, logfile="", verbose=True):
    """Allows a function to die without killing the app."""
    @functools.wraps(func)
    def p_func(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            exception = sys.exc_info()
            outer_err = inspect.stack()[-1]
            offender = inspect.trace()[-1]
            error_handler(
                exception, 
                outer_err, 
                offender, 
                logfile, 
                verbose
            )
    return p_func

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
    test(8)
    p_test = protected(test2)
    p_test(this=2)
    print("Program Still Running!")
    print(f"@protected: {protected.__doc__}")