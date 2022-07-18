
class MultiPageSelect(ui.View):
    """
        Source is of tpye
        {
            label:'',
            description:'',
            emoji:'',
            value:'' # this will be returned,
            extra: any
        }
        """
    def __init__(
        self, *, ctx: CContext = None, 
        allowed_members: Tuple[int] = (), 
        delete_items_after: bool = True, 
        timeout: Optional[float] = 180,
        select_options: List[Dict[str, Union[str,any]]] = [],
        max_retry: int = 5,
        per_page: int = 10
    ):
        super().__init__(ctx=ctx, allowed_members=allowed_members, delete_items_after=delete_items_after, timeout=timeout)
        self.select_options = select_options
        self.per_page = per_page
        
        max_pages, left_over = divmod(len(self.select_options),self.per_page)
        if left_over:
            max_pages += 1
        self.max_pages = max_pages

        self.cur_page:int = 0
        self.selected_index: int = -1
        self.selected: dict[str, Union[str, any]] = ''
        self.clear_items()
        self.intialise()
    
    def intialise(self):
        self.clear_items()
        if self.is_paginating():
            self.add_item(self._previous)
            self.add_item(self._next)
        self.add_item(self._search)
        self.add_item(self._stop)
        options = self.get_page(0)
        self._options.placeholder = f'Choose your Option ({self.cur_page+1}/{self.max_pages})'
        self._options.options = []
        for e in options:
            self._options.add_option(label=e.get('label',None), description=e.get('description',None) ,emoji=e.get('emoji',None), value=e.get('value',None))
        self.add_item(self._options)
        pass

    def is_paginating(self):
        return len(self.select_options) > self.per_page

    async def dec_page_no(self):
        if self.cur_page > 0:
            self.cur_page -= 1
            await self.render_view()

    async def inc_page_no(self):
        if self.cur_page < self.max_pages-1:
            self.cur_page += 1
            await self.render_view()

    def get_page(self, page_number):
        if self.per_page == 1:
            return self.select_options[page_number]
        else:
            base =  page_number * self.per_page
            return self.select_options[base : base+self.per_page]


    async def render_view(self):
        self.clear_items()
        if self.is_paginating():
            self.add_item(self._previous)
            self.add_item(self._next)
        self.add_item(self._search)
        self.add_item(self._stop)
        options = self.get_page(self.cur_page)
        self._options.placeholder = f'Choose your Option ({self.cur_page+1}/{self.max_pages})'
        self._options.options = []
        for e in options:
            self._options.add_option(label=e.get('label',None), description=e.get('description',None) ,emoji=e.get('emoji',None), value=e.get('value',None))
        self.add_item(self._options)
        pass
        
    async def search_item(self, text):
        """
            Missing implementation
            """

    @discord.ui.button(emoji=emotes['ctrl_previous'], style=discord.ButtonStyle.grey,row=1)
    async def _previous(self, interaction: discord.Interaction,  button: discord.ui.Button):
        await self.dec_page_no()
        await interaction.response.edit_message(view=self)
        
    @discord.ui.button(emoji=emotes['ctrl_next'], style=discord.ButtonStyle.grey,row=1)
    async def _next(self, interaction: discord.Interaction,  button: discord.ui.Button):
        await self.inc_page_no()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji=emotes['ctrl_stop'], style=discord.ButtonStyle.grey,row=1)
    async def _search(self, interaction: discord.Interaction,  button: discord.ui.Button):
        """
            Missing implementation
            """

    @discord.ui.button(emoji=emotes['ctrl_stop'], style=discord.ButtonStyle.grey,row=1)
    async def _stop(self, interaction: discord.Interaction,  button: discord.ui.Button):
        YNView = YesNoView(ctx=self.ctx)
        await interaction.response.send_message('Are you Sure?',view=YNView, ephemeral=True)
        await YNView.wait()
        if YNView.selectedOption == True:
            await self.properly_stop()
            self.stop()
        else:
            await interaction.response.defer()

    @discord.ui.select(placeholder='Choose your Option', options=[],row=0,min_values=1,max_values=1)
    async def _options(self, interaction: discord.Interaction,  select: discord.ui.Select):
        print(select.values)
        self.selected_index = int(select.values[0])
        await interaction.response.defer()
        await self.properly_stop()
        self.stop()
