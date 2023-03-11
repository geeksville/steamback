#!python3

import argparse
import logging
import os
import platform
import platformdirs
import asyncio
from . import Engine, Config, test, util, gui

"""The command line arguments"""
args = None


def main():
    """Perform command line steamback operations"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", "-d", help="Show debug log messages",
                        action="store_true")
    parser.add_argument("--test", "-t", help="Run integration code test",
                        action="store_true")
    parser.add_argument("--daemon", "-D", help="Run as a daemon that just looks for games to backup",
                        action="store_true")
    parser.add_argument("--steampath", "-s",
                        help="Ignores auto detection and force a specific Steam path")

    global args
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    logger = logging.getLogger()
    logger.info(f'Steamback running...')

    # FIXME - I bet the following will need tweaking for Windows
    plat_sys = platform.system()
    if plat_sys == "Windows":
        # DEAR WINDOWS devs - if this isn't correct you can probably fix it by doing something like https://stackoverflow.com/questions/7468061/finding-installation-directory-of-a-program-on-windows-from-python
        # please send in a pull-request if you can!
        logger.warning("""HEY! KIND TESTER! No one has tried this tool before on Windows.
                    If it works (or not) could you send an email to the author: kevinh@geeksville.com
                    If it doesn't work and you know a little python you could probably contribute an easy fix - see our github!""")
        steam_dir = os.path.join("c:/", "Program Files (x86)", "Steam")
    elif plat_sys == "Darwin":
        # DEAR osx devs - if this isn't correct you can probably fix it
        # please send in a pull-request if you can!
        logger.warning("""HEY! KIND TESTER! No one has tried this tool before on the Mac.
            If it works (or not) could you send an email to the author: kevinh@geeksville.com?
            If it doesn't work and you know a little python you could probably contribute an easy fix - see our github!""")
        steam_dir = os.path.join(os.path.expanduser(
            "~"), "Library", "Application Support", "Steam")
    else:
        steam_deck_dir = os.path.join(os.path.expanduser(
            "~"), ".local", "share", "Steam")
        steam_dir = steam_deck_dir if os.path.exists(steam_deck_dir) else os.path.join(os.path.expanduser(
            "~"), ".steam", "debian-installation")  # the default case
    if args.steampath is not None:
        steam_dir = args.steampath if os.path.isabs(
            args.steampath) else os.path.abspath(args.steampath)

    if not os.path.exists(steam_dir):
        logger.error(
            f'Can\'t find steam directory at { steam_dir }, exiting...')
        return

    app_name = "steamback"
    app_author = "geeksville"
    app_dir = platformdirs.user_data_dir(app_name, app_author)
    logger.info(f'Storing application data in { app_dir }')

    config = Config(logger, app_dir, steam_dir)
    e = Engine(config)
    e.auto_set_account_id()
    e.max_saves = 50  # On desktop UIs we can show many more saves than 10

    all_games = e.find_all_game_info()
    # print(f'All installed games: ')
    # for i in all_games:
    #    print(f'  {i}')

    if args.test:
        asyncio.run(test.testImpl(e))
    elif args.daemon:
        d = util.SteamWatcher(e)
        asyncio.run(d.run_forever())
    else:
        gui.run(e)


if __name__ == "__main__":
    main()
