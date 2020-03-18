import traceback, sys, os
import urllib.request
import urllib.parse
import re
import threading, random, sys
from ruckusTUI import ruckusTUI
from jinja2 import Environment, FileSystemLoader

import youtube_dl
import vlc

classID = random.random()
class Tube(ruckusTUI.module):
    name = "BoobTube"

    def __init__(self, app):
        # you need to start with the variables from the parent init.
        super().__init__(app)
        self.player = Player(self)
        self.templates = Environment(loader=FileSystemLoader(
            'templates', followlinks=True))
        self.classID = classID
        self.search_string = ""
        self.ind = 0
        self.topover = 0
        self.content = []
        self.search_content = []
        self.lib_content = []
        self.player_content = []
        self.link_list = []
        self.tracklist = []
        self.download_link = ""
        self.elements = []
        self.OPTIONS = {
            "quiet": True,
            'no_warnings': True,
            # "username": "",
            # "password": "", # im guessing for non youtube sites...
            # "exec_cmd": "", # ???
            "format": "bestaudio/best",
            'postprocessors': [{        
                'key': 'FFmpegExtractAudio',        
                'preferredcodec': 'mp3',        
                'preferredquality': '192',    
            }],
            "outtmpl": u"archive/youtube/%(title)s.%(ext)s",
            "noplaylist": True,
            # "progress_hooks": [hook_func],
            # 'logger': MyLogger(),
            # "download_archive": ".archive",
            # "keepvideo": False,
            "writethumbnail": True,
        }
        self.YTDL = youtube_dl.YoutubeDL(self.OPTIONS)

        self.setup()


    def setup(self):
        self.elements = ["Search", "Download", "Library", "Player"]
        self.player_elements = ["Play", "Pause", "Stop", "V-Up", "V-Down", "Next", "Prev"]

    def page_old(self, panel=None):
        panel.addstr(1,1,"Boobtube Player | v.0.1")
        # panel.bkgd(self.frontend.curses.ACS_BLOCK, self.frontend.color_cb) # w/e █ 
        # panel.bkgd(u" ", self.frontend.color_cb) # w/e █ 
        search_string = self.search_string if self.search_string else " {Press tab to type}"
        panel.addstr(2,1,f"[youtube]> "+ search_string,
            self.frontend.color_gb | self.frontend.curses.A_UNDERLINE)  # color bg white
        self.ind = 3
        l_index = 0
        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white
            if index == self.cur_el: color = self.frontend.color_rw
            panel.addstr(self.ind,2+l_index,element,color)  # color bg white
            l_index += 1 + len(element)
        self.ind += 1 # len(self.elements)
        
        ## Fix the scroller hack.            #->
        if self.scroll < 0:                  #-> This should happen in the scroll button
            self.scroll = 0                  #-> but not all mods have the content vs 
        if self.scroll >= len(self.content): #-> context b.s. going on. maybe it is the 
            self.scroll = len(self.content)  #-> most sane way to do it. hard to say.
        #################################### #->

        for index, line in enumerate(self.content):
            if index >= self.frontend.winright_dims[0]-6: 
                if self.scroll > index - 2: 
                    self.scroll = index - 2
                break
            if index-2 == self.scroll:
                panel.addstr(index+self.ind,3,line,self.frontend.palette[1])
            else:
                panel.addstr(index+self.ind,3,line,self.frontend.palette[6])
        self.ind += len(self.content)
        return False

    ##### REBUILD PAGE BUILDING PROCESS - smaller funcs #######
    def page(self, panel=None):
        self.ind = 1
        l_index = 0
        # build the selector that was initialized in the setup()
        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white
            if index == self.cur_el: color = self.frontend.color_rw
            panel.addstr(self.ind,2+l_index,element,color)  # color bg white
            l_index += 1 + len(element)
        self.ind += 1
        element = self.elements[self.cur_el]
        if element is "Search": self.search_page(panel)     #->
        elif element is "Download": self.search_page(panel) #-> should these make their own
        elif element is "Library": self.library_page(panel) #-> panels?
        elif element is "Player": self.player_page(panel)   #->
        return False
        
    def search_page(self, panel): 
        """the search page and download page will be the same."""
        ## Fix the scroller hack.                   #->
        if self.scroll < 0:                         #-> This should happen in the scroll button
            self.scroll = 0                         #-> but not all mods have the content vs 
        if self.scroll >= len(self.search_content): #-> context b.s. going on. maybe it is the 
            self.scroll = len(self.search_content)  #-> most sane way to do it. hard to say.
        ####################################        #->
        max_elements_to_display = self.frontend.winright_dims[0]-4
        ## Add the search bar
        search_string = self.search_string if self.search_string else " {Press tab to type}"
        panel.addstr(self.ind,1,f"[youtube]> "+ search_string, self.frontend.palette[7])
        self.ind += 1
        for index, line in enumerate(self.search_content):
            
            if self.scroll > self.topover + max_elements_to_display:
                self.topover += 1
            else:
                if self.topover: self.topover -= 1
            if index >= max_elements_to_display+self.topover: 
                # if self.scroll > index-2: self.scroll = index - 2
                # self.topover += 1
                break
            if index < self.topover:
                continue
            if index-1 == self.scroll:
                panel.addstr(index+self.ind,3,line,self.frontend.palette[1])
            else:
                panel.addstr(index+self.ind,3,line,self.frontend.palette[6])

    def library_page(self, panel):
        """Woah, nearly done!"""
        # check library.
        max_h = self.frontend.winright_dims[0]-4
        try:
            files = os.listdir(os.path.join(os.getcwd(), "tmp"))
            self.tracklist = [x[:-4] for x in files if x.endswith(".mp3")]
        except Exception as e:
            self.game_engine.ERROR(e)
        if self.tracklist:
            for index, track in enumerate(self.tracklist[self.topover:]):
                color = self.frontend.palette[7]
                if index+self.topover == self.scroll: 
                    color = self.frontend.palette[1]
                ## Fix the scroller hack.                   #->
                if self.scroll < 0:                         #-> This should happen in the scroll button
                    self.scroll = 0                         #-> but not all mods have the content vs 
                if self.scroll > len(self.tracklist):       #-> context b.s. going on. maybe it is the 
                    self.scroll = len(self.tracklist)       #-> most sane way to do it. hard to say.
                ####################################        #->
                
                if self.scroll > max_h+self.topover-1:
                    self.topover += 1
                    self.scroll = max_h+self.topover-1
                else: 
                    if self.topover: 
                        if self.scroll < self.topover:
                            self.topover -= 1
                if index > max_h: break
                
                panel.addstr(index+self.ind,3,track,color)

    def player_page(self, panel):
        self.ind += 1
        l_index = 0
        # build the selector that was initialized in the setup()
        for index, element in enumerate(self.player_elements):
            color = self.frontend.chess_white
            if index == self.scroll: color = self.frontend.color_rw
            panel.addstr(self.ind,2+l_index,element,color)  # color bg white
            l_index += 1 + len(element)
        self.ind += 1
        ## Fix the scroller hack.                   #->
        if self.scroll < 0:                         #-> This should happen in the scroll button
            self.scroll = 0                         #-> but not all mods have the content vs 
        if self.scroll > len(self.player_elements): #-> context b.s. going on. maybe it is the 
            self.scroll = len(self.player_elements) #-> most sane way to do it. hard to say.
        ####################################        #->

    def string_decider(self, panel, input_string):
        self.search_string = input_string

    @ruckusTUI.callback(classID, ruckusTUI.Keys.ENTER)
    def on_enter(self, *args, **kwargs):
        element = self.elements[self.cur_el]
        # panel = args[0][0]
        if "Search" in element:
            if not self.search_string:
                # self.content = ["Must Add text to search or a watch link."]
                return
            threading.Thread(target=self.search_youtube).start()
            self.search_string = ""
            
        elif "Download" in element:
            if not self.link_list:
                self.game_engine.ERROR("Search for something first.")
                return
            try:
                selected_item = self.link_list[self.scroll]
                self.download_link = selected_item
            except Exception as e:
                self.game_engine.ERROR(f"!!{e}")
                return
            try:
                self.download()
                # self.frontend.warning("Download:", f"{selected_item['title']}", self.download)
            finally:
                self.logic.selector()
            pass
        elif "Library" in element:
            target = self.tracklist[self.scroll]
            self.game_engine.ERROR(f"Loaded Track: {target}.")
            self.player(target)
        elif "Player" in element:
            button = self.player_elements[self.scroll]
            self.game_engine.ERROR(f"Player {button}")

    def download(self):
        link = self.download_link['webpage_url']
        self.game_engine.ERROR(f"Downloading: {self.download_link['title']}")
        if False:
            with self.YTDL as ydl:
                ydl.download([link])
            
    def search_youtube(self):
        """rudementary youtube search. Needs a better RE search this double lookup is dumb AF."""
        query_string = urllib.parse.urlencode({"search_query" : self.search_string})
        url = f"http://www.youtube.com/results?{query_string}"
        html_content = urllib.request.urlopen(url)
        compiled_doc = html_content.read().decode()
        search = lambda x: re.findall(r'href=\"\/watch\?v=(.{11})', x)
        search_results = list(dict.fromkeys(search(compiled_doc)))
        self.context['progress'] = 0
        self.context['max_prog'] = len(search_results)
        self.link_list = []  # reset results
        for result in search_results:
            self.context['progress'] += 1
            link = f'https://www.youtube.com/watch?v={result}'
            try:
                with self.YTDL as ydl:
                    x = ydl.extract_info(link, download=False)
                    self.link_list.append(x)
            except:
                self.game_engine.ERROR("Youtube Failure.")
                pass
        self.search_content.append("Title        | Uploader    | Date   |  Description")
        for details in self.link_list:
            # max_desc_len = self.frontend.winright_dims[1] - 13 -13 - 8 - 10
            self.search_content.append(
                f"{details['title'][:13]:13s}|{details['uploader'][:13]:13s}|{details['upload_date']}| {str(details['description'])[:30]:{30}s}"
                # f"{details['title'][:13]:13s}|{details['uploader'][:13]:13s}|{details['upload_date']}| {str(details['description'])[:max_desc_len]:{max_desc_len}s}"
                # f"{details['webpage_url']}"
            )

class Player(object):
    def __init__(self, mod):
        self.mod = mod
        self.app = mod.app
        try:
            self.i = vlc.Instance("--no-xlib")
            self.p = self.i.media_player_new()
        except:
            self.app.game_engine.ERROR("vlc is broken.")

        self.path = lambda x: os.path.join(os.getcwd(), "archive", "youtube", f"{x}.mp3")
        self.song = lambda s: self.i.media_new(self.path(s))
        
    def __call__(self, filepath): self.p.set_media(self.song(filepath))
    def play(self): return self.p.play()
    def stop(self): return self.p.stop()
    def pause(self): return self.p.pause()
    def vol_up(self): return
    def vol_down(self): return
    def next_track(self): return
    def last_track(self): return
    def shuffle(self): return
    def repeat(self): return
    def visualization(self): return