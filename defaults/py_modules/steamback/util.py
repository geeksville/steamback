import psutil
import re
import asyncio

from typing import NamedTuple
from . import Engine

"""Create a game info object: contains game_id and install_root
"""


def make_game_info(p: Engine, game_id: int) -> dict:
    # we try to use the version in the engine if possible - because it has fully validated info
    info = p.all_games.get(game_id, None)

    if not info:
        print(f'Warning: no info found for { game_id } - simulating...')
        info = {
            # On a real steamdeck there may be multiple install_roots (main vs sdcard etc) (but only one per game)
            "install_root": p.get_steam_root(),
            "game_id": game_id,
            "game_name": None
        }

    return info


"""Find running steam games and return their game IDs (only used on linux desktops - not used in decky)

Look for processes with names like this to find running steam games.  Remove any duplicates.
home.../.steam/debian-installation/ubuntu12_32/reaper SteamLaunch AppId=1318690 ...
"""


def find_running_games() -> list[int]:
    # also available in environ['SteamGameId']
    appMatch = re.compile('AppId=(.+)')
    # steam username is in environ['SteamAppUser']

    """Get the game id from a process, or None if process is not a game"""
    def get_game_id(p: psutil.Process) -> int:
        line = p.cmdline()
        if len(line) >= 3 and line[1] == "SteamLaunch":
            # environ = p.environ()
            match = appMatch.fullmatch(line[2])
            if match:
                return int(match.group(1))
        return None

    r = []
    for proc in psutil.process_iter():
        try:
            id = get_game_id(proc)
            if id:
                r.append(id)
        except psutil.AccessDenied:
            pass  # Windows won't let us see some processes
    return r


class CheckResult(NamedTuple):
    game_started: bool  # true if there is a game just started
    backed_up: list[dict]  # the games we just backed up (probably only 0 or 1)


"""Watch steam and allow async polling for game exit
"""


class SteamWatcher:
    def __init__(self, engine: Engine):
        self.was_running = set()
        self.engine = engine

    """Look for any game exits and return the saveinfo for any backups performed
    """
    async def check_once(self) -> CheckResult:
        running = set(find_running_games())

        # set of games that just started
        started = running - self.was_running

        # set of games that just stopped
        stopped = self.was_running - running

        backups = []
        for game_id in stopped:
            info = make_game_info(self.engine, game_id)
            b = await self.engine.do_backup(info)
            if b is not None:
                backups.append(b)

        # get ready for next time
        self.was_running = running
        return CheckResult(game_started=len(started) > 0, backed_up=backups)

    async def run_forever(self):
        self.engine.logger.info(
            "Watching Steam for game exit, press Ctrl-C to quit...")
        while True:
            await asyncio.sleep(5)
            await self.check_once()
