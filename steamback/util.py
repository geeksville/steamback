import psutil, re, asyncio, os
from . import Engine

"""Create a game info object: contains game_id and install_root
"""
def make_game_info(p: Engine, game_id: int, name: str = None) -> dict:
    info = {
        # On a real steamdeck there may be multiple install_roots (main vs sdcard etc) (but only one per game)
        "install_root": p.get_steam_root(),
        "game_id": game_id,
        "game_name": name
    }
    return info

"""Find running steam games and return their game IDs (only used on linux desktops - not used in decky)

Look for processes with names like this to find running steam games.  Remove any duplicates.
home.../.steam/debian-installation/ubuntu12_32/reaper SteamLaunch AppId=1318690 ...
"""
def find_running_games() -> list[int]:
    appMatch = re.compile('AppId=(.+)') # also available in environ['SteamGameId']
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

    procs = map(get_game_id, psutil.process_iter())
    r = filter(lambda p: p is not None, procs)
    return r

async def backup_daemon(engine: Engine):
    was_running = set()
    while True:
        await asyncio.sleep(5)
        running = set(find_running_games())

        # set of games that just started
        started = running - was_running

        # set of games that just stopped
        stopped = was_running - running

        for game_id in stopped:
            info = make_game_info(engine, game_id)
            await engine.do_backup(info)

        # get ready for next time
        was_running = running