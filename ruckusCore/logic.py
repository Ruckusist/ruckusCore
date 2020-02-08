class Logic(object):
    def __init__(self, engine):
        self.engine = engine  # access to the kill switch.
        self.working_panels = []       # the list of pointers
        self.cur = 0                   # the current working panel
        self.available_panels = {}     # V.2 of this idea.

    # def setup_panels(self):
    #     """Creates a Stack of Panels that can be .top()'ed for a UX """
    #     # if not self.engine.app.menu: sys.exit("WTF!")
    #     if self.engine.app.menu:
    #         for label, page, string_decider, mod in self.engine.app.menu:
    #             self.working_panels.append((
    #                 self.engine.frontend.make_panel(
    #                     self.engine.frontend.winright_dims,
    #                     label,  # Item is a Title String.
    #                     True),  # is scrollable
    #                 page, string_decider, mod))
        
    #     if self.working_panels:
    #         for panel, page, _, _ in self.working_panels:
    #             p = page(panel[0])
    #             if p:
    #                 for index, line in enumerate(p.split('\n')):
    #                     if index > self.engine.frontend.winright_dims[0]-2: break
    #                     panel[0].addstr(index+1, 1, line[:self.engine.frontend.winright_dims[1]-2])

    def setup_panel(self, mod):
        self.available_panels[mod.name] = [
                mod,
                self.engine.frontend.make_panel(
                    self.engine.frontend.winright_dims,
                    mod.name,  # Item is a Title String.
                    True),     # is scrollable
            ]

    def setup_panels(self):
        for mod in self.engine.app.menu:
            self.setup_panel(mod)
            
        self.all_page_update()

    def all_page_update(self):
        self.engine.frontend.redraw_window(self.engine.frontend.winleft)

        for index, mod_name in enumerate(list(self.available_panels)):
            color = self.engine.frontend.color_rw if index == self.cur else self.engine.frontend.color_cb
            message = lambda x: self.engine.frontend.winleft[0].addstr(index+1, 1, x, color)
            mod = self.available_panels[mod_name][0]
            if not mod.visible: continue
            panel = self.available_panels[mod_name][1]
            message(mod.name)
            rendered_page = mod.page(panel[0])
            
            if rendered_page:  # or did the page render itself??
                for index, line in enumerate(rendered_page.split('\n')):
                    if index > self.engine.frontend.winright_dims[0]-2: break
                    panel[0].addstr(index+1, 1, line[:self.engine.frontend.winright_dims[1]-2])
            
            if index == self.cur:
                panel[1].top()

        # and update the header.
        head_text = self.engine.app.header()
        head_panel = self.engine.app.frontend.header
        if not self.engine.error_timeout:
            head_panel[0].addstr(1,1,head_text, self.engine.frontend.palette[3])

        # and update the footer.
        self.redraw_footer()


    """  DEPRICATED
    def all_page_update(self):
        # limits
        w = self.engine.frontend.winright_dims[1]
        h = self.engine.frontend.winright_dims[0]
        for panel, page, _, _ in self.working_panels:
            # THis is probably a horrible idea, redrawing the screen is costing
            # a lot of FPS. cant say if its super useful.
            self.engine.frontend.redraw_window(panel)
            p = page(panel[0])
            if p:
                for index, line in enumerate(p.split('\n')):
                    if index >= h-2: break
                    panel[0].addstr(index+1, 1, line[:w-2])
        
        # and update the header.
        head_text = self.engine.app.header()
        head_panel = self.engine.app.frontend.header
        if not self.engine.error_timeout:
            head_panel[0].addstr(1,1,head_text, self.engine.frontend.palette[3])

        # and update the footer.
        self.redraw_footer()
    """

    # def selector(self):
    #     """Menu Selection functions."""
    #     self.engine.frontend.redraw_window(self.engine.frontend.winleft)
    #     # self.engine.frontend.header[0].addstr(1, 15, "<cur: {cur}>".format(cur=self.cur))
    #     for index, (item, _, _, _) in enumerate(self.engine.app.menu):
    #         if self.cur == index:
    #             self.engine.frontend.winleft[0].addstr(index+1, 1, item, self.engine.frontend.color_rw)
    #         else:
    #             self.engine.frontend.winleft[0].addstr(index+1, 1, item, self.engine.frontend.color_cb)

    #     self.working_panels[self.cur][0][1].top()

    def redraw_footer(self):
        # TODO: THIS NEEDS TO BE ANOTHER THING...
        if self.engine.frontend.screen_mode:
            options = ["|q| to quit   |Tab| switch Mode   |enter| to start service", "|pgUp| change menu |pgDn| change menu"]
        else:
            options = [" Cool stuff goes here...", "|enter| submit   |'stop'| to kill service"]
        self.engine.frontend.redraw_window(self.engine.frontend.debug)
        self.engine.frontend.debug[0].addstr(1, 1, options[0], self.engine.frontend.color_gb)
        self.engine.frontend.debug[0].addstr(2, 1, options[1], self.engine.frontend.color_gb)

    def end_safely(self):
        # for _, _, _, mod in self.working_panels:
        #     mod.end_safely()

        for mod_name in list(self.available_panels):
            mod = self.available_panels[mod_name][0]
            mod.end_safely()

    def decider(self, keypress):
        """Callback decider system."""
        mod_g = self.available_panels[
            list(self.available_panels)[self.cur]
        ]
        mod = mod_g[0]
        panel = mod_g[1]
        app_callbacks = self.engine.app.callbacks
        if type(keypress) is str: 
            mod.string_decider(panel, keypress)
            # self.selector()
            return
        if int(keypress) < 1: return
        try:
            all_calls_for_button =\
                list(filter(lambda d: d['key'] in [keypress], app_callbacks))
            call_for_button =\
                list(filter(lambda d: d['classID'] in [mod.classID,0,1], all_calls_for_button))[0]
        except Exception as e:
            self.engine.ERROR(f"k: {keypress} has no function")
            return
        try:
            callback = call_for_button['func']
            callback(mod, panel)
        except Exception as e:
            self.engine.ERROR(f"{call_for_button['func'].__name__} | {e}")
