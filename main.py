import logging
import shutil
import os
import json

logging.basicConfig(filename="/tmp/deckshot.log",
                    format='[Deckshot] %(asctime)s %(levelname)s %(message)s',
                    filemode='w+',
                    force=True)
logger=logging.getLogger()

# logger.setLevel(logging.INFO) # can be changed to logging.DEBUG for debugging issues
# can be changed to logging.DEBUG for debugging issues

# FIXME use os.environ["DECKY_PLUGIN_RUNTIME_DIR"] to find our prefs dir, if not defined assume desktop testing

logger.setLevel(logging.DEBUG)

is_decky = True if os.environ["DECKY_PLUGIN_RUNTIME_DIR"] else False

class Plugin:
    def __init__(self):
        self.account_id = 0
        self.dry_run = False # Set to true to suppress 'real' writes to directories  
        # FIXME not yet implemented
        # self.ignore_unchanged = True # don't generate backups if the files haven't changed since last backup

    async def set_account_id(self, id_num: int):
        self.account_id = id_num
        pass

    """
    Return the saves directory path (creating it if necessary)
    """
    def _get_savesdir(self) -> str:
        e = os.environ["DECKY_PLUGIN_RUNTIME_DIR"]

        # We want to allow testing when not running under decky
        r = e if e else "/tmp/deckshot"
    
        p = os.path.join(r, "saves")
        if not os.path.exists(p):
            os.makedirs(p)
        return p

    """
    Return the path to the game directory for a specified game
    """
    def _get_gamedir(self, game_id: int):
        return "/home/deck/.local/share/Steam/userdata" if is_decky else "/home/kevinh/.steam/debian-installation/userdata"

    """
    Read the vdf file for the specified game, or if not found return None
    """
    def _read_vdf(self, game_id: int) -> dict:
        d = self._get_gamedir(game_id)
        path = os.path.join(d, "remotecache.vdf")
        with open(path) as f:
            d = json.load(f)
            return d

    def _copy_by_vdf(self, vdf: dict, src_dir: str, dest_dir: str):
        # shutil.copyfile(src_file, save_path)
        pass

    """
    Create a save file directory save-GAMEID-timestamp and return SaveInfo object
    """
    def _create_savedir(self, game_id: int, is_undo: bool = False) -> dict:
        return {}

    """
    we keep only the most recent undo and the most recent 10 saves
    """
    async def _cull_old_saves(self):
        infos = self.get_saveinfos()

        # If more than one undo, delete the oldest
        # if more than 10 saves, delete the oldest
        # shutil.rmtree(path)
        
        pass

    """
    Given a save_info return a full pathname to that directory
    """
    def _saveinfo_to_dir(self, save_info: dict) -> str:
        d = self._get_savesdir()
        return os.path.join(d, save_info.filename)

        """
        Parse a filename and return a saveinfo dict.  saveinfo contains: filename, is_undo, game_id
        """
    def _file_to_saveinfo(self, filename: str) -> dict:
        i = {}
        return i

    """
    Backup a particular game.

    Returns a new SaveInfo object or None if no backup was needed or possible
    SaveInfo is a dict with filename, game_id, timestamp, is_undo
    """
    async def do_backup(self, game_id: int) -> dict:
        saveInfo = self._create_savedir(game_id)
        gameDir = self._get_gamedir(game_id)
        vdf = self._read_vdf(game_id)

        self._copy_by_vdf(vdf, gameDir, self._saveinfo_to_dir(saveInfo))

        await self._cull_old_saves() 
        return saveInfo

    """
    Restore a particular savegame using the saveinfo object
    """
    async def do_restore(self, save_info: dict):
        gameDir = self._get_gamedir(save_info.game_id)
        undoInfo = self._create_savedir(game_id, is_undo = True)

        # first make the backup
        self._copy_by_vdf(vdf, gameDir, self._saveinfo_to_dir(undoInfo))

        # then restore from our old snapshot
        self._copy_by_vdf(vdf, self._saveinfo_to_dir(save_info), gameDir)

        await self._cull_old_saves() # we now might have too many undos, so possibly delete one

    """
    Return all available saves, newest save first and undo as the absolute first

    Returns an array of SaveInfo objects
    """
    async def get_saveinfos(self) -> list[dict]:
        dir = self._get_savesdir()
        return [ "fish" ]

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        logger.info("Deckshot running!")
    
    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        logger.info("Deckshot exiting!")





