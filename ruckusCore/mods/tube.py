import re, threading, random, os, pathlib
import urllib.request
import urllib.parse
from lxml import etree
import ruckusCore
import youtube_dl


classIDTUBE = random.random()
class Tube(ruckusCore.Module):
    name = "Boobtube"
    def __init__(self, app):
        super().__init__(app)
        self.classID = classIDTUBE

        self.elements = self.elements = ["Search", "Download", "Library", "Player"]
        self.player_elements  = ["Play", "Pause", "Stop", "V-Up", "V-Down", "Next", "Prev"]
        self.index = 1  # Verticle Print Position
        self.tube_path = self.tubePath = os.path.join(self.app.app_path, 'tube')
        if not os.path.exists(self.tube_path): os.makedirs(self.tube_path)
        self.search_string = ""
        self.content = []
        self.search_content = []
        self.lib_content = []
        self.player_content = []
        self.link_list = []
        self.tracklist = []
        self.download_link = ""
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
            "outtmpl": u"{0}/%(title)s.%(ext)s".format(self.tube_path),
            "noplaylist": True,
            # "progress_hooks": [hook_func],
            # 'logger': MyLogger(),
            # "download_archive": ".archive",
            # "keepvideo": False,
            "writethumbnail": True,
        }
        self.YTDL = youtube_dl.YoutubeDL(self.OPTIONS)

    def page(self, panel):
        # panel.addstr(1,1,"Boobtube Player | v.0.2")
        self.index = 1  # reset this to the top of the box every round

        # HORIZONTAL SCROLLER
        h_index = 0  # HORIZONTAL index
        for index, element in enumerate(self.elements):
            color = self.frontend.chess_white if index is not self.cur_el else self.frontend.color_rw
            panel.addstr(self.index, 2+h_index, element, color)
            h_index += 1 + len(element)

        self.index += 1  # increment the Verticle Print Position
        # panel.addstr(self.index, 4, "NEXT THING", self.frontend.chess_white)
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
        panel.addstr(self.index,1,f"[youtube] >"+ search_string, self.frontend.palette[7])
        self.index += 1
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
                panel.addstr(index+self.index,3,line,self.frontend.palette[1])
            else:
                panel.addstr(index+self.index,3,line,self.frontend.palette[6])

    def library_page(self, panel):
        """Woah, nearly done!"""
        # check library.
        max_h = self.frontend.winright_dims[0]-4
        try:
            files = os.listdir(self.tube_path)
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

                panel.addstr(index+self.index,3,track,color)

    def player_page(self, panel):
        self.index += 1
        l_index = 0
        # build the selector that was initialized in the setup()
        for index, element in enumerate(self.player_elements):
            color = self.frontend.chess_white
            if index == self.scroll: color = self.frontend.color_rw
            panel.addstr(self.index,2+l_index,element,color)  # color bg white
            l_index += 1 + len(element)
        self.index += 1
        ## Fix the scroller hack.                   #->
        if self.scroll < 0:                         #-> This should happen in the scroll button
            self.scroll = 0                         #-> but not all mods have the content vs
        if self.scroll > len(self.player_elements): #-> context b.s. going on. maybe it is the
            self.scroll = len(self.player_elements) #-> most sane way to do it. hard to say.
        ####################################        #->

    def string_decider(self, panel, input_string):
        self.search_string = input_string

    @ruckusCore.callback(classIDTUBE, ruckusCore.Keys.ENTER)
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
                # self.logic.selector()
                pass
            pass
        elif "Library" in element:
            target = self.tracklist[self.scroll]
            self.game_engine.ERROR(f"Loaded Track: {target}.")
            self.player(target)
        elif "Player" in element:
            button = self.player_elements[self.scroll]
            self.game_engine.ERROR(f"Player {button} -- working!")

    def download(self):
        link = self.download_link['webpage_url']
        self.game_engine.ERROR(f"Downloading: {self.download_link['title']}")
        if True:
            with self.YTDL as ydl:
                ydl.download([link])

    def search_youtube(self):
        """rudementary youtube search. Needs a better RE search this double lookup is dumb AF."""
        query_string = urllib.parse.urlencode({"search_query" : self.search_string})
        lurl = f"http://www.youtube.com/results?{query_string}"
        html_content = urllib.request.urlopen(lurl)
        compiled_doc = html_content.read().decode()
        
        dom = etree.HTML(compiled_doc)
        sections = dom.xpath('//div[contains(@class, "yt-lockup-content")]')

        # search_results = []
        # for section in sections:
        #     url = list(section.xpath('.//a[contains(@href, "/watch")]')[0]
            # search_results.append( {
            #     "url": url, # section.xpath('.//a[contains(@href, "/watch")]')[0],
            #     "title": ''.join(url.itertext()),
            #     "desc": list(section.xpath('./div[contains(@class, "yt-lockup-description")]')),
            #     "meta": list(section.xpath('./div[contains(@class, "yt-lockup-meta")]')),
            #     "uploader": list(section.xpath('.//a[contains(@href, "/user/")]'))
            # } )
        # search = lambda x: re.findall(r'href=\"\/watch\?v=(.{11})', x)
        # search_results = list(dict.fromkeys(search(compiled_doc)))
        # self.context['progress'] = 0
        # self.context['max_prog'] = len(search_results)
        # self.link_list = []  # reset results
        # for result in search_results:
        #     self.context['progress'] += 1
        #     link = f'https://www.youtube.com/watch?v={result}'
        #     try:
        #         with self.YTDL as ydl:
        #             x = ydl.extract_info(link, download=False)
        #             self.link_list.append(x)
        #     except:
        #         self.game_engine.ERROR("Youtube Failure.")
        #         pass
        # self.search_content.append("Title        | Uploader    |  Description")

        # for details in search_results:
        #     self.search_content.append(
        #         f"{details.get('title', 'None')[:13]:13s}|"+\
        #         f"{details.get('uploader', 'None')[:13]:13s}"+\
        #         f"{details.get('desc', 'None')}[:30]:{30}s"
        #     )


        # for details in self.link_list:
        #     # max_desc_len = self.frontend.winright_dims[1] - 13 -13 - 8 - 10
        #     self.search_content.append(
        #         f"{details['title'][:13]:13s}|{details['uploader'][:13]:13s}|{details['upload_date']}| {str(details['description'])[:30]:{30}s}"
        #         # f"{details['title'][:13]:13s}|{details['uploader'][:13]:13s}|{details['upload_date']}| {str(details['description'])[:max_desc_len]:{max_desc_len}s}"
        #         # f"{details['webpage_url']}"
        #     )


if __name__ == "__main__":
    app = ruckusCore.App([Tube])
    try:
        ruckusCore.protected(app.run())
    finally:
        app.game_engine.exit_program()
