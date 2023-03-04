#!python3


import tkinter
from tkinter import ttk 
import sv_ttk
from async_tkinter_loop import async_handler, main_loop
import asyncio
from . import Engine

class GUI:
  

    def __init__(self, master: tkinter.Tk, e: Engine):
        self.master = master
        self.engine = e
        master.title("Steamback")

        """ self.label_index = 0
        self.label_text = StringVar()
        self.label_text.set(self.LABEL_TEXT[self.label_index])
        self.label = Label(master, textvariable=self.label_text)
        self.label.bind("<Button-1>", self.cycle_label_text)
        self.label.pack() """

        self.greet_button = ttk.Button(master, text="Greet", command=self.greet)
        self.greet_button.pack()

        self.close_button = ttk.Button(master, text="Close", command=master.quit)
        self.close_button.pack()

        # create listbox object
        self.supported_games = tkinter.Listbox(master, 
                        # bg="grey",
                        # activestyle='dotbox'
                        )

        # Define the size of the window.
        master.geometry("300x250")

        # Define a label for the list.
        label = ttk.Label(master, text="Supported Games")

        # pack the widgets
        label.pack()
        self.supported_games.pack()

    async def find_supported(self):
        all_games = self.engine.find_all_game_info()
        print(f'All installed games: ')
        for i in all_games:
            print(f'  {i}')

        # Test find_supported
        supported = await self.engine.find_supported(all_games)
        print(f'Supported games: ')
        for i, g in enumerate(supported):
            print(f'  {i} {g}')
            self.supported_games.insert(i, g["game_name"])

    async def async_main_loop(self):
        # do this in the background - update gui when done
        asyncio.create_task(self.find_supported())

        await main_loop(self.master)

    def greet(self):
        print("Greetings!")

"""
    def cycle_label_text(self, event):
        self.label_index += 1
        self.label_index %= len(self.LABEL_TEXT)  # wrap around
        self.label_text.set(self.LABEL_TEXT[self.label_index])
"""

def run(e: Engine):

    root = tkinter.Tk()

    # to make tk less ugly https://www.reddit.com/r/Python/comments/lps11c/how_to_make_tkinter_look_modern_how_to_use_themes/
    # style = Style(root)
    # Set the theme with the theme_use method
    # style.theme_use('clam')  # put the theme name here, that you want to use
    sv_ttk.set_theme("dark")

    g = GUI(root, e)
    # async_mainloop(root)

    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(g.async_main_loop())
