import random, os
import time
from timeit import default_timer as timer
from operator import itemgetter
from wifi import Cell, Scheme
import wifi
import threading
import RPi.GPIO as gpio
from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader

classID = random.random()
class Wifi(ruckusTUI.module):
    """My Raspi Control Module."""

    name = "Wifi Scanner"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)
        self.classID = classID
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        self.should_loop = False
        self.ind = 1
        self.listlen = 0
        self.context['scantime'] = 0
        self.context['wifilist'] = []
        self.context['known_wifi'] = [{
            "ssid": "Ruckus",
            "password": "eric2344"
            },
            {
            "ssid": "WhalenWifi",
            "password": "bella2344"	
        }]
        self.context['select'] = 0
        if not os.path.exists(os.path.join(os.getcwd(), "archive", "wifi")):
            os.mkdir(os.path.join(os.getcwd(), "archive", "wifi"))
        self.setup()

    def setup(self):
        self.elements = ["Scan", "Attack", "Library", "Connect"]

    def loop(self):
        while True:
            self.context['looping'] = "True"
            if not self.should_loop:
                break
            self.get_all_cells()
            if self.scroll > len(self.context['wifilist']):
                self.scroll = 0
            if self.scroll < 0:
                self.scroll = len(self.context['wifilist'])
            self.context['select'] = self.scroll
        self.context['looping'] = "False"

    def get_all_cells(self):
        try:
            start_scan = timer()
            scan = []
            for index, cell in enumerate(Cell.all('wlan0')):
                scan.append( {
	                "index": index,
                    "ssid": cell.ssid,
                    "signal": cell.signal,
                    "quality": cell.quality,
                    "address": cell.address,
                    "encrypted": cell.encryption_type if cell.encrypted else "None"
                    } )
            self.context['wifilist'] = scan
            #self.context['wifilist'] = sorted(
            #    self.context['wifilist'],
            #    key=itemgetter("signal"),
            #    reverse = True
            #)
        except Exception as e:
            self.app.log.append(e)
            pass
        self.context['scantime'] = timer() - start_scan

    @ruckusTUI.callback(classID, ruckusTUI.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        if self.should_loop:
            self.should_loop = False
        else:
            self.should_loop = True
            # self.app.log.append("Starting Wifi Scan")
            threading.Thread(target=self.loop).start()

    def end_safely(self):
        self.should_loop = False

    def page_old(self, panel=None):
        template = self.templates.get_template("wifi.j2")
        return template.render(context=self.context)

    def page(self, panel=None):
        l_index = 0
        #### POPULATE LIBRARY FOR ALL TABS    #->
        with open(os.path.join(os.getcwd(), "archive", "wifi", "known.wifi"), "w+") as lib:
            self.library = lib.readlines()

        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white
            if index == self.cur_el: color = self.frontend.color_rw
            panel.addstr(1, 2+l_index, str(element), color)  # color bg white
            l_index += 1 + len(element)
        self.ind = 2
        element = self.elements[self.cur_el]
        if element is "Scan": self.scan_page(panel)          #->
        elif element is "Attack": self.attack_page(panel)    #-> should these make their own
        elif element is "Library": self.library_page(panel)  #-> panels?
        elif element is "Connect": self.connect_page(panel)  #->
        return False

    def scan_page(self, panel):
        # list elements one color at a time.
        # first color = cyan
        # if True: return
        if self.context['wifilist']:
            ## Fix the scroller hack.                   #->
            if self.scroll < 0:                         #-> This should happen in the scroll button
                self.scroll = 0                         #-> but not all mods have the content vs 
            if self.scroll > len(self.context["wifilist"]): #-> context b.s. going on. maybe it is the 
                self.scroll = len(self.context["wifilist"]) #-> most sane way to do it. hard to say.
            ####################################        #->
            header = "SSID                Signal     inLibrary     Encryption"
            panel.addstr(self.ind, 3, header, self.frontend.palette[4])
            panel.addstr(self.ind+1, 3, "-"*60, self.frontend.palette[4])
            self.ind += 2
            for index, result in enumerate(self.context['wifilist']):
                max_elements_to_display = self.frontend.winright_dims[0]-4
                if index >= max_elements_to_display: break
                color = self.frontend.palette[3]
                if index == self.scroll: color = self.frontend.color_rw
                ssid = result["ssid"].strip("\\x00")
                if not ssid: ssid = "--> MYSTERY! **"
                panel.addstr(index+self.ind, 3, ssid[:19], color)
                color = self.frontend.palette[2]
                if index == self.scroll: color = self.frontend.color_rw
                signal = str(result["signal"]) +" dBm"
                panel.addstr(index+self.ind, 23, signal, color)
        return

    def attack_page(self, panel): return
    def library_page(self, panel): return
    def connect_page(self, panel): return