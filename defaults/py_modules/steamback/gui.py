#!python3


from tkinter import *
from tkinter import ttk
import sv_ttk
import datetime
import timeago
import os
from async_tkinter_loop import async_handler
import asyncio
from . import Engine, util

logger = None


def add_scrollbar(view: ttk.Treeview) -> ttk.Scrollbar:
    root = view.master
    b = ttk.Scrollbar(root,
                      orient="vertical",
                      command=view.yview)

    # Configuring treeview
    view.configure(yscrollcommand=b.set)

    return b


async def main_loop(root: Tk) -> None:
    """
    An asynchronous implementation of tkinter mainloop
    :param root: tkinter root object
    :return: nothing
    """
    try:
        while True:
            try:
                root.winfo_exists()  # Will throw TclError if the main window is destroyed
                root.update()
            except TclError:
                break

            # Don't poll events quickly if not visible and not the focus of the user
            # no longer checking root.state() == 'normal'
            interval = 0.05 if root.focus_displayof() else 0.5
            await asyncio.sleep(interval)
    except TclError as e:
        if not "application has been destroyed" in str(e):
            print(f'Exiting due to { e }')


def saveinfo_ago_str(si: dict) -> str:
    # our timestamps are in msecs
    now = datetime.datetime.now()
    ts = datetime.datetime.fromtimestamp(si["timestamp"] / 1000.0)
    ts_str = timeago.format(ts, now)
    return ts_str


class GUI:

    def __init__(self, root: Tk, e: Engine):
        self.root = root
        self.engine = e
        self.watcher = util.SteamWatcher(e)

        # A dictionary mapping from saveinfo filename to saveinfo dictionary object
        self.saves = None

        # The saveinfo for the undo file
        self.undo = None

        self.set_app_icon()

        root.title("Steamback")
        root.resizable(width=800, height=400)

        """Save window position on exit"""

        def on_close():
            # Here I write the X Y position of the window to a file "myapp.conf"
            with open(os.path.join(self.engine.config.app_data_dir, "window.conf"), "w") as conf:
                conf.write(root.geometry())

            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)

        # Here I read the X and Y positon of the window from when I last closed it.
        try:
            with open(os.path.join(self.engine.config.app_data_dir, "window.conf"), "r") as conf:
                root.geometry(conf.read())
        except Exception:
            pass  # Ignore any errors (file might be missing etc)

        """ self.label_index = 0
        self.label_text = StringVar()
        self.label_text.set(self.LABEL_TEXT[self.label_index])
        self.label = Label(root, textvariable=self.label_text)
        self.label.bind("<Button-1>", self.cycle_label_text)
        self.label.pack() """

        # self.greet_button = ttk.Button(root, text="Greet", command=self.greet)
        # self.greet_button.pack()

        # self.close_button = ttk.Button(root, text="Close", command=root.quit)
        # self.close_button.pack()

        self.undo_button = ttk.Button(
            root, text="Undo changes to XXX", command=async_handler(self.on_undo_click))
        self.revert_button = ttk.Button(
            root, text="Revert XXX to save from 5 minutes ago", command=async_handler(self.on_revert_click))

        # Define a label for the list.
        self.status = ttk.Label(
            root, text="Status: Watching Steam for game exit...")

        # List supported games
        treev = ttk.Treeview(root,
                             selectmode='browse'
                             # bg="grey",
                             # activestyle='dotbox'
                             )
        self.supported_games = treev

        s_sb = add_scrollbar(treev)

        # Defining number of columns
        treev["columns"] = ("name",)

        # Defining heading
        treev['show'] = 'headings'
        treev.heading("name", text="Supported Games")

        # List supported games
        treev = ttk.Treeview(root,
                             selectmode='none'
                             # bg="grey",
                             # activestyle='dotbox'
                             )
        self.supported_games = treev

        games_sb = add_scrollbar(treev)

        # Defining number of columns
        treev["columns"] = ("name",)

        # Defining heading
        treev['show'] = 'headings'
        treev.heading("name", text="Supported Games")

        char_width = 8
        treev.column("name", minwidth=char_width * 10,
                     width=char_width * 30, stretch=YES)

        # List save games
        treev = ttk.Treeview(root,
                             selectmode='browse'
                             # bg="grey",
                             # activestyle='dotbox'
                             )
        self.save_games = treev

        saves_sb = add_scrollbar(treev)

        # Defining number of columns
        treev["columns"] = ("name", "time")

        # Defining heading
        treev['show'] = 'headings'
        treev.heading("name", text="Save games")
        treev.heading("time", text="Time")

        treev.column("name", minwidth=char_width * 10,
                     width=char_width * 30, stretch=YES)
        treev.column("time", minwidth=char_width * 6,
                     width=char_width * 15, stretch=NO)

        treev.bind("<<TreeviewSelect>>", self.on_savegame_selected)

        # Do the layout per this great documentation: https://tkdocs.com/tutorial/grid.html

        self.supported_games.grid(
            row=0, column=0, sticky=(N, S, W, E), rowspan=3)
        games_sb.grid(row=0, column=1, sticky=(N, S), rowspan=3)

        self.save_games.grid(row=0, column=3, sticky=(N, S, E, W), rowspan=1)
        saves_sb.grid(row=0, column=4, sticky=(N, S), rowspan=1)

        # Position the various undo/revert buttons but hide them for now
        self.undo_button.grid(row=1, column=3, padx=8, pady=8)
        self.revert_button.grid(row=2, column=3, padx=8, pady=8)
        self.undo_button.grid_remove()
        self.revert_button.grid_remove()

        self.status.grid(row=10, sticky=(W, E), padx=8, pady=8)

        root.rowconfigure(0, weight=1)

        # grow the currently empty middle space
        root.columnconfigure(0, weight=1)
        root.columnconfigure(2, weight=1)
        root.columnconfigure(3, weight=1)

    """A savegame was selected in the treeview"""

    def on_savegame_selected(self, event):
        for filename in self.save_games.selection():
            si = self.saves[filename]

            # set revert button text
            self.revert_button.config(
                text=f'Revert { si["game_info"]["game_name"]} to save from { saveinfo_ago_str(si)}')

            self.revert_button.grid()  # show revert button

    """user clicked to restore from a savegame"""

    async def on_revert_click(self):
        for filename in self.save_games.selection():

            # do the restore
            si = self.saves[filename]
            # self.engine.dry_run = True  # FIXME - testing
            await self.engine.do_restore(si)

            # Set status msg
            new_text = f'Reverted to { si["game_info"]["game_name"] } snapshot'
            self.set_status(new_text)

            # deselect the item the user just reverted
            self.save_games.selection_remove(filename)
            self.revert_button.grid_remove()

            # We just generated an undo save, so update the list of savegames
            await self.find_savegames()

    """User wants to undo our last revert"""

    async def on_undo_click(self):
        # do the restore
        si = self.undo
        assert si

        # self.engine.dry_run = True  # FIXME - testing
        await self.engine.do_restore(si)

        # Set status msg
        new_text = f'Undid changes to { si["game_info"]["game_name"] }'
        self.set_status(new_text)

    async def find_supported(self):
        all_games = self.engine.find_all_game_info()

        supported = await self.engine.find_supported(all_games)
        tree = self.supported_games
        # put all children into the args of this function call
        tree.delete(*tree.get_children())
        for g in supported:
            tree.insert(
                "", END, values=(g["game_name"], ))

    async def find_savegames(self):
        all_saves = await self.engine.get_saveinfos()

        # Don't list any undos in the tree view
        saveinfos = list(filter(lambda i: not i["is_undo"], all_saves))
        undos = list(filter(lambda i: i["is_undo"], all_saves))

        self.saves = {si["filename"]: si for si in saveinfos}

        # show undo button as needed
        if len(undos) > 0:
            g = undos[0]
            self.undo = g
            self.undo_button.config(
                text=f'Undo changes to { g["game_info"]["game_name"]}')
            self.undo_button.grid()

        # fill the treeview
        # put all children into the args of this function call
        tree = self.save_games
        tree.delete(*tree.get_children())
        for g in saveinfos:
            # print(f'  {g}')
            tree.insert(
                "", END, iid=g["filename"], values=(g["game_info"]["game_name"], saveinfo_ago_str(g)))

    """Look for steam changes, and then queue up looking again"""
    async def watch_steam(self):
        # self.engine.ignore_unchanged = False  # for testing
        backups = await self.watcher.check_once()

        if (len(backups) > 0):
            si = backups[0]  # only print for first one (the common case)
            new_text = f'Save-game snapshot taken for { si["game_info"]["game_name"] }...'
            await self.find_savegames()
            self.set_status(new_text)

        # Our run is exiting, but queue one for the future
        quitting = False
        if not quitting:
            await asyncio.sleep(5)
            asyncio.create_task(self.watch_steam())

    def set_status(self, new_text):
        self.status.config(text=new_text)

    async def async_main_loop(self):
        # do this in the background - update gui when done
        asyncio.create_task(self.find_supported())
        asyncio.create_task(self.find_savegames())
        asyncio.create_task(self.watch_steam())

        await main_loop(self.root)

    """Set the icon for our app in GUI"""

    def set_app_icon(self):
        # might be missing on some systems so use a try catch and do the imports here
        try:
            from PIL import Image, ImageTk
            with Image.open(os.path.join(os.path.dirname(
                    __file__),  'data', 'icons8-refresh-96.png')) as ico:
                photo = ImageTk.PhotoImage(ico)
                self.root.wm_iconphoto(True, photo)
        except Exception as e:
            logger.warning(
                f'Can\'t set application icon due to missing library: {e}')


"""
    def cycle_label_text(self, event):
        self.label_index += 1
        self.label_index %= len(self.LABEL_TEXT)  # wrap around
        self.label_text.set(self.LABEL_TEXT[self.label_index])
"""


def run(e: Engine):
    global logger
    logger = e.config.logger

    root = Tk()

    # to make tk less ugly https://www.reddit.com/r/Python/comments/lps11c/how_to_make_tkinter_look_modern_how_to_use_themes/
    # style = Style(root)
    # Set the theme with the theme_use method
    # style.theme_use('clam')  # put the theme name here, that you want to use
    sv_ttk.set_theme("dark")

    g = GUI(root, e)
    # async_mainloop(root)

    asyncio.get_event_loop_policy().get_event_loop(
    ).run_until_complete(g.async_main_loop())
