#!python3

from typing import NamedTuple
import re
import json
import time
import os
import shutil
import logging
import re
import traceback
from pathlib import Path


logger = None

"""Try to parse a valve vdf file.  Returning all key/value pairs it finds as string pairs.
Note: this doesn't preserve hierarchy - only keys are checked
"""


def _parse_vcf(path: str) -> dict:
    kvMatch = re.compile('\s*"(.+)"\s+"(.+)"\s*')
    d = {}
    with open(path) as f:
        for line in f:
            # ignore leading/trailing space.  Now ideal like looks like "key"   "value"
            m = kvMatch.fullmatch(line)
            if m:
                d[m.group(1)] = m.group(2)
    return d


class Config(NamedTuple):
    logger: logging.Logger
    app_data_dir: str  # where app specific data files are stored
    steam_dir: str  # the root of the Steam data files


class Engine:
    def __init__(self, config: Config):
        global logger
        logger = config.logger
        # logger.setLevel(logging.INFO) # can be changed to logging.DEBUG for debugging issues
        # can be changed to logging.DEBUG for debugging issues

        self.config = config
        # try:
        #    os.environ["DECKY_PLUGIN_RUNTIME_DIR"]
        #    logger.info('Running under decky')
        # except:

        logger.info(f'Steamback engine created: { config }')

        # a dict from gameid -> gameinfo for all installed games.  ONLY USED ON DESKTOP not DECKY
        self.all_games = None
        self.account_id = 0
        self.dry_run = False  # Set to true to suppress 'real' writes to directories

        # don't generate backups if the files haven't changed since last backup
        self.ignore_unchanged = True

    def set_account_id(self, id_num: int):
        logger.debug(f'Setting account id { id_num } on { self }')
        self.account_id = id_num

    """Find the steam account ID for the current user (and)

    We look for a directory in userdata/accountname.  If there are multiple account names we currently throw an exception
    eventually we could look at the config file in each of those dirs to see which one was touched most recently.
    """

    def auto_set_account_id(self) -> int:
        files = os.listdir(os.path.join(self.get_steam_root(), "userdata"))
        ids = list(filter(lambda i: i is not None, map(
            lambda f: int(f) if f.isnumeric() and f != "0" else None, files)))
        assert len(ids) == 1  # Is there exactly one account dir?
        id = ids[0]
        self.set_account_id(id)
        return id

    """
    Return the saves directory path (creating it if necessary)
    """

    def _get_savesdir(self) -> str:
        # we now use a new directory for saves (because metaformat changed) - original version was never released
        p = os.path.join(self.config.app_data_dir, "saves2")
        if not os.path.exists(p):
            os.makedirs(p)
        # logger.debug(f'Using saves directory { p }')
        return p

    """
    Return the steam root directory
    """

    def get_steam_root(self) -> str:
        return self.config.steam_dir

    """
    Return the path to the game directory for a specified game
    """

    def _get_gamedir(self, game_id: int) -> str:
        assert self.account_id  # better be set by now
        return os.path.join(self.get_steam_root(), "userdata", str(self.account_id), str(game_id))

    """return true if the game is installed on external storage
    """

    def _is_on_mmc(self, game_info: dict) -> bool:
        assert game_info["install_root"]
        return game_info["install_root"].startswith("/run")

    """read installdir from appmanifest_gameid.vdf and return it

    is_system_dir is True if instead of the game install loc you'd like us to search the system steam data
    """

    def _get_steamapps_dir(self, game_info: dict, is_system_dir: bool = False) -> str:
        assert game_info["install_root"]
        d = game_info["install_root"] if not is_system_dir else self.get_steam_root()
        steamApps = os.path.join(d, "steamapps")
        return steamApps

    """read installdir from appmanifest_gameid.vdf and return it (or None if not found)
    """

    def _parse_installdir(self, game_info: dict) -> str:
        app_dir = self._get_steamapps_dir(game_info)
        vcf = _parse_vcf(os.path.join(
            app_dir, f'appmanifest_{ game_info["game_id"] }.acf'))
        install_dir = vcf.get("installdir", None)
        return install_dir

    """Return all games that can be found on this system (only used for python apps - when in Decky this comes from JS)
    """

    def find_all_game_info(self) -> list[dict]:
        steam_dir = self.get_steam_root()
        app_dir = os.path.join(steam_dir, "steamapps")
        files = filter(lambda f: f.startswith("appmanifest_")
                       and f.endswith(".acf"), os.listdir(app_dir))
        r = []
        rdict = {}  # a dict from game id int to the gameinfo object
        for f in files:
            vcf = _parse_vcf(os.path.join(app_dir, f))
            id = vcf.get("appid", None)
            name = vcf.get("name", None)
            if id and name:
                id = int(id)
                info = {
                    # On a real steamdeck there may be multiple install_roots (main vs sdcard etc) (but only one per game)
                    "install_root": steam_dir,
                    "game_id": id,
                    "game_name": name
                }
                r.append(info)
                rdict[id] = info

        self.all_games = rdict
        return r

    """
    Find the root directory for where savegames might be found for either windows or linux

    is_system_dir is True if instead of the game install loc you'd like us to search the system steam data
    """

    def _get_game_saves_root(self, game_info: dict, is_linux_game: bool, is_system_dir: bool = False) -> list[str]:
        steamApps = self._get_steamapps_dir(game_info, is_system_dir)

        if is_linux_game:
            installdir = self._parse_installdir(game_info)
            rootdir = os.path.join(steamApps, "common", installdir)
        else:
            rootdir = os.path.join(
                steamApps, f'compatdata/{ game_info["game_id" ] }/pfx/drive_c/users/steamuser')

        return rootdir

    """
    Find all directories that contain steam_autocloud.vdf files or None
    """

    def _find_autoclouds(self, game_info: dict, is_linux_game: bool) -> list[str]:
        root_dir = self._get_game_saves_root(game_info, is_linux_game)

        p = Path(root_dir)
        files = p.rglob("steam_autocloud.vdf")
        # we want the directories that contained the autocloud
        dirs = list(map(lambda f: str(f.parent), files))

        # logger.debug(f'Autoclouds in { root_dir } are { dirs }')
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
        # FIXME what about paths where someone used / in the filename!
        dirSplit = rPrefix.rfind('/')
        if dirSplit != -1:
            # throw away everything after the last slash (and the slash itself)
            rPrefix = rPrefix[:dirSplit]

            # check the last n characters of autocloud and if they match our prefix, strip them to find the new root
            autoTail = autocloud[-len(rPrefix):]
            if autoTail == rPrefix:
                autocloud = autocloud[:-len(rPrefix)]

        return autocloud

    """
    Look in the likely locations for savegame files (per the rcf list). return that path or None
    """

    def _search_likely_locations(self, game_info: dict, rcf: list[str]) -> str:
        roots = []

        def addRoots(is_system_dir: bool):
            # try relative to the linux root
            roots.append(self._get_game_saves_root(
                game_info, is_linux_game=True, is_system_dir=is_system_dir))

            # try relative to Documents or application data on windows
            r = self._get_game_saves_root(
                game_info, is_linux_game=False, is_system_dir=is_system_dir)
            windowsRoots = ['Documents',
                            'Application Data', 'AppData/LocalLow', 'Local Settings/Application Data']
            for subdir in windowsRoots:
                d = os.path.join(r, subdir)
                roots.append(d)

        # look in the system directory first (if we might also have savegames on the mmc)
        if (self._is_on_mmc(game_info)):
            addRoots(True)

        addRoots(False)

        logger.debug(f'Searching roots { roots }')
        for r in roots:
            if self._rcf_is_valid(r, rcf):
                return r

        return None

    """
    Try to figure out where this game stores its save files. return that path or None
    """

    def _find_save_games(self, game_info, rcf: list[str]) -> str:
        d = self._get_gamedir(game_info["game_id"])

        # First check to see if the game uses the 'new' "remote" directory approach to save files (i.e. they used the steam backup API from the app)
        fullRemotes = (os.path.join(d, x)
                       for x in ["remote", "ac/LinuxXdgDataHome"])
        remoteFound = next((x for x in fullRemotes if os.path.isdir(x)), None)
        if remoteFound:
            # Store the savegames directory for this game
            return remoteFound

        # okay - now check the standard doc roots for games - do this before looking for autoclouds because it is more often the match
        d = self._search_likely_locations(game_info, rcf)
        if (d):
            return d

        # Alas, now we need to scan the install dir to look for steam_autocloud.vdf files.  If found that means the dev is doing the 'lazy'
        # way of just saying "backup all files due to some path we enter in our web admin console".

        # FIXME, cache this expensive result
        autoclouds = self._find_autoclouds(game_info, is_linux_game=True)

        # Not found on linux, try looking in windows
        if not autoclouds:
            autoclouds = self._find_autoclouds(game_info, is_linux_game=False)

        # If no/multiple autocloud files are found, just search in the root and see if that works
        if not autoclouds or len(autoclouds) != 1:
            return None

        return self._find_save_root_from_autoclouds(game_info, rcf, autoclouds[0])

    """ 
    confirm that at least one savegame exists, to validate our assumptions about where they are being stored
    if no savegame found claim we can't back this app up.
    """

    def _rcf_is_valid(self, root_dir: str, rcf: list[str]):
        for f in rcf:
            full = os.path.join(root_dir, f)
            if os.path.isfile(full):
                logger.debug(f'RCF is valid { root_dir }')
                return True
            else:
                # logger.debug(f'RCF file not found { full }')
                pass
        # logger.debug(f'RCF invalid { root_dir }')
        return False

    """
    Read the rcf file for the specified game, or if not found return None
    """

    def _read_rcf(self, game_info: dict) -> list[str]:
        d = self._get_gamedir(game_info["game_id"])
        path = os.path.join(d, "remotecache.vdf")
        # logger.debug(f'Read rcf {path}')

        rcf = []
        if os.path.isfile(path):
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

        # logger.debug(f'Read rcf with { len(rcf) } entries')

        # If we haven't already found where the savegames for this app live, do so now (or fail if not findable)
        if not "save_games_root" in game_info:
            saveRoot = self._find_save_games(game_info, rcf)
            if not saveRoot:
                logger.warning(
                    f'Unable to backup { game_info }: not yet supported')
                return None
            else:
                game_info["save_games_root"] = saveRoot

        # confirm that at least one savegame exists, to validate our assumptions about where they are being stored
        # if no savegame found claim we can't back this app up.
        if not self._rcf_is_valid(game_info["save_games_root"], rcf):
            logger.debug(
                f'RCF seems invalid, not backing up { game_info }')
            return None

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
        numCopied = 0
        for k in rcf:
            spath = os.path.join(src_dir, k)

            # if the filename contains directories - create them
            if os.path.exists(spath):
                numCopied = numCopied + 1
                dpath = os.path.join(dest_dir, k)
                # logger.debug(f'Copying file { k }')
                if not self.dry_run:
                    dir = os.path.dirname(dpath)
                    os.makedirs(dir, exist_ok=True)
                    shutil.copy2(spath, dpath)
            else:
                # logger.warning(f'Not copying missing file { k }')
                pass
        logger.info(
            f'Copied { numCopied } files from { src_dir } to { dest_dir }')

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
        # logger.debug(f'Creating savedir {path}, {si}')
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
            # logger.debug(f'Parsed filename {filename} as {si}')
            return si

    """ delete the savedir and associated json
    """

    def _delete_savedir(self, filename):
        shutil.rmtree(os.path.join(
            self._get_savesdir(), filename), ignore_errors=True)
        try:
            os.remove(os.path.join(self._get_savesdir(), filename + ".json"))
        except OSError:
            pass

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
                # if not self.dry_run: we ignore dryrun for culling otherwise our test system dir fills up
                self._delete_savedir(todel["filename"])

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
        logger.info(f'Attempting backup of { game_info }')
        rcf = self._read_rcf(game_info)

        if not rcf:
            return None

        game_id = game_info["game_id"]
        newest_save = await self._get_newest_save(game_id)
        if newest_save and self.ignore_unchanged:
            game_timestamp = self._get_rcf_timestamp(rcf, game_info)
            if newest_save["timestamp"] > game_timestamp:
                logger.warning(
                    f'Skipping backup for { game_id } - no changed files')
                return None

        saveInfo = self._create_savedir(game_info)
        try:
            gameDir = self._get_game_root(game_info)
            # logger.info(f'got gamedir { gameDir }')
            self._copy_by_rcf(rcf, gameDir, self._saveinfo_to_dir(saveInfo))
        except:
            # Don't keep old directory/json around if we encounter an exception
            self._delete_savedir(saveInfo["filename"])
            raise  # rethrow

        await self._cull_old_saves()
        return saveInfo

    """
    Restore a particular savegame using the saveinfo object
    """
    async def do_restore(self, save_info: dict):
        # logger.debug(f'In do_restore for { save_info }')
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
    Given a list of game_infos, return a list of game_infos which are supported for backups
    """
    async def find_supported(self, game_infos: list) -> list[dict]:
        # if we get any sort of exception while scanning a particular game info, keep trying the others
        def try_rcf(info):
            try:
                # logger.debug(f'try_rcf { info }')
                return self._read_rcf(info)
            except Exception as e:
                logger.error(
                    f'Error scanning rcf for {info}, exception { traceback.format_exc() }')
                return None

        # logger.debug(f'find supported { game_infos }')
        supported = list(filter(try_rcf, game_infos))
        return supported

    """
    Return all available saves, newest save first and undo as the absolute first

    Returns an array of SaveInfo objects
    """
    async def get_saveinfos(self) -> list[dict]:
        dir = self._get_savesdir()
        files = filter(lambda f: f.endswith(".json"), os.listdir(dir))

        def attempt_saveinfo(f: str) -> dict:
            try:
                si = self._file_to_saveinfo(f)
                return si
            except Exception as e:
                logger.error(f'Error reading JSON for {f}, {e}')
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
