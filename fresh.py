import os, asyncio
import curses

class Window(object):
    """The Alphagriffin Curses frontend template."""

    def __init__(self, stdscr=None):
        """Setup basic curses interface."""
        if stdscr is None:
            stdscr = curses.initscr()
        self.curses = curses
        self.screen = stdscr
        self.palette = []
        curses.start_color()
        # curses.use_default_colors()
        self.setup_color()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0) # 0: invisible, 1: visible, 2: bright
        self.screen.keypad(1)
        self.screen.nodelay(1)
        self.screen_h, self.screen_w = self.screen.getmaxyx()
        self.screen_mode = True

    def get_input(self):
        """Pass curses control capture to another class."""
        x = 0
        # self.footer[0].addstr(1, 1, "Mode: KeyStroke")
        # self.screen.nodelay(True)
        if self.screen_mode:
            x = self.screen.getch()
            try:
                if int(x) > 0:
                    self.keystroke(x)
            except: pass
        else:
            self.screen.keypad(0)
            curses.echo()
            self.redraw_window(self.footer)
            x = self.footer[0].getstr(1, 1).decode('UTF-8')
            self.screen.keypad(1)
            curses.noecho()
            self.screen_mode = True
            self.redraw_window(self.footer)
        return x

    def setup_color(self):
        """Load a custom theme."""
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.color_rw = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        self.color_cb = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.color_gb = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_RED)
        self.chess_black = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_WHITE)
        self.chess_white = curses.color_pair(5)
        self.color_bold = curses.A_BOLD
        self.color_blink = curses.A_BLINK
        self.color_error = self.color_bold | self.color_blink | self.color_rw
        # Palette of all available colors... == 8 wtf
        try:
            for i in range(0, curses.COLORS):
                if i == 0: curses.init_pair(i+1, i, curses.COLOR_WHITE)
                else: curses.init_pair(i+1, i, curses.COLOR_BLACK)
                self.palette.append(curses.color_pair(i))
        except:
            print("failing to setup color!")
            for i in range(0, 7):
               if i == 0: curses.init_pair(i+1, i, curses.COLOR_WHITE)
               else: curses.init_pair(i+1, i, curses.COLOR_BLACK)
               self.palette.append(curses.color_pair(i))
            pass
        finally:
            # print(f"len(curses.COLORS) = {len(self.palette)}")
            # time.sleep(2)
            pass

    def end_safely(self):
        """Return control to the shell."""
        curses.nocbreak()
        self.screen.keypad(0)
        curses.echo()
        curses.endwin()


if __name__ == '__main__':
    app = Window()
    app.end_safely()