import logging
import shutil
import os
import time
import re

logging.basicConfig(filename="/tmp/deckshot.log",
                    format='[Deckshot] %(asctime)s %(levelname)s %(message)s',
                    filemode='w+',
                    force=True)
logger=logging.getLogger()

# logger.setLevel(logging.INFO) # can be changed to logging.DEBUG for debugging issues
# can be changed to logging.DEBUG for debugging issues

# FIXME use os.environ["DECKY_PLUGIN_RUNTIME_DIR"] to find our prefs dir, if not defined assume desktop testing

logger.setLevel(logging.DEBUG)

is_decky = True

class Plugin:
    def __init__(self):
        global is_decky
        is_decky = hasattr(os.environ, "DECKY_PLUGIN_RUNTIME_DIR") # env vars seem to not be set till later
        self.account_id = 0
        self.dry_run = False # Set to true to suppress 'real' writes to directories  
        # FIXME not yet implemented
        self.ignore_unchanged = True # don't generate backups if the files haven't changed since last backup

    async def set_account_id(self, id_num: int):
        if not isinstance(self, Plugin):
            logger.warn('self is not an instance, fixing')
            self = pinstance

        self.account_id = id_num
        pass

    """
    Return the saves directory path (creating it if necessary)
    """
    def _get_savesdir(self) -> str:
        # We want to allow testing when not running under decky
        r = os.environ["DECKY_PLUGIN_RUNTIME_DIR"] if is_decky else "/tmp/deckshot"
    
        p = os.path.join(r, "saves")
        if not os.path.exists(p):
            os.makedirs(p)
        # logger.debug(f'Using saves directory { p }')
        return p

    """
    Return the path to the game directory for a specified game
    """
    def _get_gamedir(self, game_id: int) -> str:
        r = "/home/deck/.local/share/Steam/userdata" if is_decky else "/home/kevinh/.steam/debian-installation/userdata"
        return os.path.join(r, str(self.account_id), str(game_id))

    """
    Read the vdf file for the specified game, or if not found return None
    """
    def _read_vdf(self, game_id: int) -> list:
        d = self._get_gamedir(game_id)
        path = os.path.join(d, "remotecache.vdf")

        if not os.path.isdir(os.path.join(d, "remote")):
            logger.warn(f'Unable to backup { game_id }: not yet supported') # We currently only understand games that have their saves in teh 'remote' subdir
            return None

        if os.path.isfile(path):
            logger.debug(f'Read vdf {path}')
            with open(path) as f:
                s = f.read() # read full file as a string
                lines = s.split('\n') 
                # logger.debug(f'file is {lines}')

                # drop first two lines because they are "gameid" {
                lines = lines[2:]
                # We look for lines containing quotes and immediately preceeding lines with just an open brace
                prevl = None
                r = []
                skipping = False
                for l in lines:
                    s = l.strip()
                    if skipping: # skip the contents of {} records
                        if s == "}":
                            skipping = False
                    elif s == "{":
                        if prevl:
                            # prevl will have quote chars as first and last of string.  Remove them
                            filename = (prevl[1:])[:-1]
                            r.append(filename)
                            prevl = None

                        # Now skip until we get a close brace
                        skipping = True
                    else:
                        prevl = s

                # logger.debug(f'vdf files are {r}')
                return r
        else:
            logger.debug(f'No vdf {path}')
            return None

    """
    Parse valve vdf json objects and copy named files

    {
	"ChangeNumber"		"-6703994677807818784"
	"ostype"		"-184"
	"my games/XCOM2/XComGame/SaveData/profile.bin"
	{
		"root"		"2"
		"size"		"15741"
		"localtime"		"1671427173"
		"time"		"1671427172"
		"remotetime"		"1671427172"
		"sha"		"df59d8d7b2f0c7ddd25e966493d61c1b107f9b7a"
		"syncstate"		"1"
		"persiststate"		"0"
		"platformstosync2"		"-1"
	}
    """
    def _copy_by_vdf(self, vdf: list, src_dir: str, dest_dir: str):
        logger.debug(f'Copying from { src_dir } to { dest_dir }')
        for k in vdf:
            spath = os.path.join(src_dir, 'remote', k) # We currently only work with saves in this directory

            # if the filename contains directories - create them
            if os.path.exists(spath):
                dpath = os.path.join(dest_dir, k)
                logger.debug(f'Copying file { k }')
                if not self.dry_run:
                    dir = os.path.dirname(dpath)
                    os.makedirs(dir, exist_ok=True)
                    shutil.copy2(spath, dpath)
            else:
                logger.warn(f'Not copying missing file { k }')

    """
    Get full paths to existing files mentioned in vdf.
    """
    def _get_vdf_paths(self, vdf: list, src_dir: str) -> list:
        # We currently only work with saves in this directory
        paths = map(lambda k: os.path.join(src_dir, 'remote', k), vdf)
        paths = list(filter(lambda p: os.path.exists(p), paths))
        return paths

    """
    Find the timestamp of the most recently updated file in a vdf
    """
    def _get_vdf_timestamp(self, vdf: list, src_dir: str) -> int:
        full = self._get_vdf_paths(vdf, src_dir)
        m_times = list(map(lambda f: os.path.getmtime(f), full))
        max_time = int(round(max(m_times) * 1000)) # we use msecs not secs
        return max_time

    """
    Create a save file directory save-GAMEID-timestamp and return SaveInfo object
    """
    def _create_savedir(self, game_id: int, is_undo: bool = False) -> dict:

        ts = int(round(time.time() * 1000))  # msecs since 1970
        filename = f'{ "undo" if is_undo else "save" }_{ game_id }_{ ts }'

        i = self._file_to_saveinfo(filename)

        path = self._saveinfo_to_dir(i)
        logger.debug(f'Creating savedir {path}')
        if not self.dry_run:
            os.makedirs(path, exist_ok = True)
        return i

    """
    Parse a filename and return a saveinfo dict.  
    """
    def _file_to_saveinfo(self, filename: str) -> dict:
        l = filename.split("_")
        i = {
            "is_undo": l[0] == "undo",
            "game_id": int(l[1]),
            "timestamp": int(l[2]),
            "filename": filename
            }
        # logger.debug(f'Parsed filename {i}')
        return i

    """
    we keep only the most recent undo and the most recent 10 saves
    """
    async def _cull_old_saves(self):
        infos = await self.get_saveinfos()

        undos = list(filter(lambda i: i["is_undo"], infos))
        saves = list(filter(lambda i: not i["is_undo"], infos))

        def delete_oldest(files, to_keep):
            while len(files) > to_keep:
                todel = files.pop()
                logger.info(f'Culling { todel }')
                if not self.dry_run:
                    shutil.rmtree(os.path.join(self._get_savesdir(), todel["filename"]))
        
        delete_oldest(undos, 1)
        delete_oldest(saves, 10)

    """
    Given a save_info return a full pathname to that directory
    """
    def _saveinfo_to_dir(self, save_info: dict) -> str:
        d = self._get_savesdir()
        return os.path.join(d, save_info["filename"])

    """
    Get the newest saveinfo for a specified game (or None if not found)
    """
    async def _get_newest_save(self, game_id):
        infos = await self.get_saveinfos()

        # Find first matching item or None
        newest = next(
            (x for x in infos if x["game_id"] == game_id and not x["is_undo"]), None)
        return newest

    """
    Backup a particular game.

    Returns a new SaveInfo object or None if no backup was needed or possible
    SaveInfo is a dict with filename, game_id, timestamp, is_undo
    """
    async def do_backup(self, game_id: int) -> dict:
        logger.info(f'Attempting backup of { game_id }')
        logger.info(f'self is { self } gameid is { game_id } typ { type(game_id)}')

        if not isinstance(self, Plugin):
            logger.warn('self is not an instance, fixing')
            self = pinstance

        game_id = int(game_id) # force int type, javascript comes across as strs
        gameDir = self._get_gamedir(game_id)
        logger.info(f'got gamedir { gameDir }')
        vdf = self._read_vdf(game_id)

        if not vdf:
            return None
        
        newest_save = await self._get_newest_save(game_id)
        if newest_save and self.ignore_unchanged:
            game_timestamp = self._get_vdf_timestamp(vdf, gameDir)
            if newest_save["timestamp"] > game_timestamp:
                logger.warn(f'Skipping backup for { game_id } - no changed files')
                return None

        saveInfo = self._create_savedir(game_id)
        self._copy_by_vdf(vdf, gameDir, self._saveinfo_to_dir(saveInfo))

        await self._cull_old_saves() 
        return saveInfo

    """
    Restore a particular savegame using the saveinfo object
    """
    async def do_restore(self, save_info: dict):
        logger.info(f'Attempting restore of { save_info }')
        game_id = save_info["game_id"]
        vdf = self._read_vdf(game_id)
        assert vdf
        gameDir = self._get_gamedir(game_id)
        
        # first make the backup (unless restoring from an undo already)
        if not save_info["is_undo"]:
            undoInfo = self._create_savedir(game_id, is_undo=True)
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
        files = os.listdir(dir)
        infos = list(map(lambda f: self._file_to_saveinfo(f), files))

        # Sort by timestamp, newest first
        infos.sort(key = lambda i: i["timestamp"], reverse = True)

        # put undos first
        undos = list(filter(lambda i: i["is_undo"], infos))
        saves = list(filter(lambda i: not i["is_undo"], infos))
        infos = undos + saves
        return infos

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        logger.info("Deckshot running!")
    
    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        logger.info("Deckshot exiting!")


pinstance = Plugin()
