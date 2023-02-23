import re
import json
import time
import os
import shutil
import logging
from pathlib import Path

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin

logger = decky_plugin.logger

# logger.setLevel(logging.INFO) # can be changed to logging.DEBUG for debugging issues
# can be changed to logging.DEBUG for debugging issues

logger.setLevel(logging.DEBUG)

is_decky = True

pinstance = None

"""Work around for busted decky creation"""


def fixself(self) -> object:
    global pinstance

    if not isinstance(self, Plugin):
        logger.warn('self is not an instance, fixing')
        if not pinstance:
            pinstance = Plugin()
        self = pinstance
    return self


class Plugin:
    def __init__(self):
        global is_decky
        try:
            os.environ["DECKY_PLUGIN_RUNTIME_DIR"]
            logger.info('Running under decky')
        except:
            is_decky = False  # if we didn't throw that envar is set
            logger.info('Simulating decky')

        self.account_id = 0
        self.dry_run = False  # Set to true to suppress 'real' writes to directories
        # FIXME not yet implemented
        # don't generate backups if the files haven't changed since last backup
        self.ignore_unchanged = True

    async def set_account_id(self, id_num: int):
        self = fixself(self)

        self.account_id = id_num
        pass

    """
    Return the saves directory path (creating it if necessary)
    """

    def _get_savesdir(self) -> str:
        # We want to allow testing when not running under decky
        r = os.environ["DECKY_PLUGIN_RUNTIME_DIR"] if is_decky else "/tmp/steamback"

        # we now use a new directory for saves (because metaformat changed) - original version was never released
        p = os.path.join(r, "saves2")
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
    Find all directories that contain steam_autocloud.vdf files or None
    """

    def _find_autoclouds(self, game_info, is_linux_game: bool) -> list[str]:
        assert game_info["install_root"]
        steamApps = os.path.join(game_info["install_root"], "steamapps")

        if is_linux_game:
            assert game_info["game_name"]
            rootdir = os.path.join(steamApps, "common", game_info["game_name"])
        else:
            rootdir = os.path.join(
                steamApps, f'compatdata/{ game_info["game_id" ] }/pfx/drive_c/users/steamuser')

        p = Path(rootdir)
        files = p.rglob("steam_autocloud.vdf")
        # we want the directories that contained the autocloud
        dirs = list(map(lambda f: str(f.parent), files))

        logger.debug(f'Autoclouds in { rootdir } are { dirs }')
        return dirs

    """
    Try to figure out where this game stores its save files. return that path or None
    """

    def _find_save_root_from_autoclouds(self, game_info, rcf, autocloud: str) -> str:

        if len(rcf) < 1:
            return None     # No backup files in the rcf, we can't even do the scan

        # Find any common prefix (which is a directory path) that is shared by all entries in the rcf filenames
        prevR = rcf[0]
        firstDifference = len(prevR)
        for r in rcf:
            # find index of first differing char (or None if no differences)
            index = next(
                (i for i in range(min(len(prevR), len(r))) if prevR[i] != r[i]), None)

            if index is not None and firstDifference > index:
                firstDifference = index

            prevR = r

        # common prefix for all files in rdf (could be empty if files were all backed up from autocloud dir)
        rPrefix = prevR[:firstDifference]

        # at this point rPrefix is _probably_ a directory like "SNAppData/SavedGames/" but it also could be
        # "SNAppData/SavedGames/commonPrefix" (in the case where all the backup files started with commonPrefix)
        # therefore scan backwards from end of string to find first / and then we KNOW everything left of that
        # is a directory.  If we don't find such a slash, that means none of the backup files are using directories
        # and we should just use the existing autocloud dir.
        dirSplit = rPrefix.rfind('/') # FIXME what about paths where someone used / in the filename!
        if dirSplit != -1:
            rPrefix = rPrefix[:dirSplit] # throw away everything after the last slash (and the slash itself)

            # check the last n characters of autocloud and if they match our prefix, strip them to find the new root
            autoTail = autocloud[-len(rPrefix):] 
            if autoTail == rPrefix:
                autocloud = autocloud[:-len(rPrefix)]

        return autocloud

    """
    Try to figure out where this game stores its save files. return that path or None
    """

    def _find_save_games(self, game_info, rcf: list[str]) -> str:
        d = self._get_gamedir(game_info["game_id"])

        # First check to see if the game uses the 'new' "remote" directory approach to save files (i.e. they used the steam backup API from the app)
        remoteSaveGames = os.path.join(d, "remote")
        if os.path.isdir(remoteSaveGames):
            # Store the savegames directory for this game
            return remoteSaveGames

        # Alas, now we need to scan the install dir to look for steam_autocloud.vdf files.  If found that means the dev is doing the 'lazy'
        # way of just saying "backup all files due to some path we enter in our web admin console".

        # FIXME, cache this expensive result
        autoclouds = self._find_autoclouds(game_info, is_linux_game=True)
        if not autoclouds:
            autoclouds = self._find_autoclouds(game_info, is_linux_game=False)

        if not autoclouds or len(autoclouds) == 0:
            logger.warn(f'No autocloud found for { game_info }, can\'t backup')
            return None

        # We currently (but could someday?) don't support multiple autocloud directories
        if len(autoclouds) > 1:
            logger.warn(
                f'Multiple autoclouds found for { game_info }, can\'t backup')
            return None

        return self._find_save_root_from_autoclouds(game_info, rcf, autoclouds[0])

    """
    Read the rcf file for the specified game, or if not found return None
    """

    def _read_rcf(self, game_info: dict) -> list[str]:
        d = self._get_gamedir(game_info["game_id"])
        path = os.path.join(d, "remotecache.vdf")

        rcf = []
        if os.path.isfile(path):
            logger.debug(f'Read rcf {path}')
            with open(path) as f:
                s = f.read()  # read full file as a string
                lines = s.split('\n')
                # logger.debug(f'file is {lines}')

                # drop first two lines because they are "gameid" {
                lines = lines[2:]
                # We look for lines containing quotes and immediately preceeding lines with just an open brace
                prevl = None

                skipping = False
                for l in lines:
                    s = l.strip()
                    if skipping:  # skip the contents of {} records
                        if s == "}":
                            skipping = False
                    elif s == "{":
                        if prevl:
                            # prevl will have quote chars as first and last of string.  Remove them
                            filename = (prevl[1:])[:-1]
                            rcf.append(filename)
                            prevl = None

                        # Now skip until we get a close brace
                        skipping = True
                    else:
                        prevl = s
        else:
            logger.debug(f'No rcf {path}')
            return None

        # If we haven't already found where the savegames for this app live, do so now (or fail if not findable)
        if not "save_games_root" in game_info:
            saveRoot = self._find_save_games(game_info, rcf)
            if not saveRoot:
                logger.warn(
                    f'Unable to backup { game_info }: not yet supported')
                return None
            else:
                game_info["save_games_root"] = saveRoot

        # logger.debug(f'rcf files are {r}')
        return rcf

    """Get the root directory this game uses for its save files
    """

    def _get_game_root(self, game_info: dict) -> str:
        return game_info["save_games_root"]

    """
    Parse valve rcf json objects and copy named files

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

    def _copy_by_rcf(self, rcf: list, src_dir: str, dest_dir: str):
        logger.debug(f'Copying from { src_dir } to { dest_dir }')
        for k in rcf:
            spath = os.path.join(src_dir, k)

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
    Find the timestamp of the most recently updated file in a rcf
    """

    def _get_rcf_timestamp(self, rcf: list, game_info: dict) -> int:
        src_dir = self._get_game_root(game_info)

        # Get full paths to existing files mentioned in rcf.
        paths = map(lambda k: os.path.join(src_dir, k), rcf)
        full = list(filter(lambda p: os.path.exists(p), paths))

        m_times = list(map(lambda f: os.path.getmtime(f), full))
        max_time = int(round(max(m_times) * 1000))  # we use msecs not secs
        return max_time

    """
    Create a save file directory save-GAMEID-timestamp and return SaveInfo object
    Also write the sister save-GAMEID-timestamp.json metadata file
    """

    def _create_savedir(self, game_info: dict, is_undo: bool = False) -> dict:
        game_id = game_info["game_id"]
        assert game_info["save_games_root"]  # This better be populated by now!
        ts = int(round(time.time() * 1000))  # msecs since 1970

        si = {
            "game_info": game_info,
            "timestamp": ts,
            "filename": f'{ "undo" if is_undo else "save" }_{ game_id }_{ ts }',
            "is_undo": is_undo
        }

        path = self._saveinfo_to_dir(si)
        logger.debug(f'Creating savedir {path}, {si}')
        if not self.dry_run:
            os.makedirs(path, exist_ok=True)
            with open(path + ".json", 'w') as fp:
                json.dump(si, fp)

        return si

    """
    Load a savesaveinfo.json from the saves directory
    """

    def _file_to_saveinfo(self, filename: str) -> dict:
        dir = self._get_savesdir()
        with open(os.path.join(dir, filename)) as j:
            si = json.load(j)
            logger.debug(f'Parsed filename {filename} as {si}')
            return si

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
                    shutil.rmtree(os.path.join(
                        self._get_savesdir(), todel["filename"]))

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
            (x for x in infos if x["game_info"]["game_id"] == game_id and not x["is_undo"]), None)
        return newest

    """
    Backup a particular game.

    Returns a new SaveInfo object or None if no backup was needed or possible
    SaveInfo is a dict with filename, game_id, timestamp, is_undo
    game_info is a dict of game_id and install_root
    """
    async def do_backup(self, game_info: dict) -> dict:
        self = fixself(self)

        logger.info(f'Attempting backup of { game_info }')
        rcf = self._read_rcf(game_info)

        if not rcf:
            return None

        game_id = game_info["game_id"]
        newest_save = await self._get_newest_save(game_id)
        if newest_save and self.ignore_unchanged:
            game_timestamp = self._get_rcf_timestamp(rcf, game_info)
            if newest_save["timestamp"] > game_timestamp:
                logger.warn(
                    f'Skipping backup for { game_id } - no changed files')
                return None

        saveInfo = self._create_savedir(game_info)
        gameDir = self._get_game_root(game_info)
        logger.info(f'got gamedir { gameDir }')
        self._copy_by_rcf(rcf, gameDir, self._saveinfo_to_dir(saveInfo))

        await self._cull_old_saves()
        return saveInfo

    """
    Restore a particular savegame using the saveinfo object
    """
    async def do_restore(self, save_info: dict):
        self = fixself(self)
        game_info = save_info["game_info"]
        rcf = self._read_rcf(game_info)
        assert rcf
        gameDir = self._get_game_root(game_info)

        # first make the backup (unless restoring from an undo already)
        if not save_info["is_undo"]:
            logger.info('Generating undo files')
            undoInfo = self._create_savedir(game_info, is_undo=True)
            self._copy_by_rcf(rcf, gameDir, self._saveinfo_to_dir(undoInfo))

        # then restore from our old snapshot
        logger.info(f'Attempting restore of { save_info }')
        self._copy_by_rcf(rcf, self._saveinfo_to_dir(save_info), gameDir)

        # we now might have too many undos, so possibly delete one
        await self._cull_old_saves()

    """
    Given a list of game_infos, return a list of game-ids which are supported for backups
    """
    async def find_supported(self, game_infos: list):
        self = fixself(self)
        supported = list(filter(lambda info: self._read_rcf(info), game_infos))
        return supported

    """
    Return all available saves, newest save first and undo as the absolute first

    Returns an array of SaveInfo objects
    """
    async def get_saveinfos(self) -> list[dict]:
        self = fixself(self)
        dir = self._get_savesdir()
        files = filter(lambda f: f.endswith(".json"), os.listdir(dir))

        def attempt_saveinfo(f: str) -> dict:
            try:
                si = self._file_to_saveinfo(f)
                return si
            except Exception as e:
                logger.warn(f'Error reading JSON for {f}, {e}')
                return None

        infos = list(filter(lambda f: f is not None, map(
            lambda f: attempt_saveinfo(f), files)))

        # Sort by timestamp, newest first
        infos.sort(key=lambda i: i["timestamp"], reverse=True)

        # put undos first
        undos = list(filter(lambda i: i["is_undo"], infos))
        saves = list(filter(lambda i: not i["is_undo"], infos))
        infos = undos + saves
        return infos

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        logger.info("Steamback running!")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        logger.info("Steamback exiting!")


"""
    This seems busted for me so leaving off for now... -geeksville
    
    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/template.log`
        decky_plugin.migrate_logs(os.path.join(decky_plugin.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
        decky_plugin.migrate_settings(
            os.path.join(decky_plugin.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        decky_plugin.migrate_runtime(
            os.path.join(decky_plugin.DECKY_HOME, "template"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-template"))
"""
