import sys, os, asyncio

sys.path.append(os.path.realpath(".."))
sys.path.append('../../decky-loader/plugin')

from main import *


"""Create a game info object: contains game_id and install_root
"""


def make_game_info(game_id: int) -> dict:
    info = {
        # On a real steamdeck there may be multiple install_roots (main vs sdcard etc) (but only one per game)
        "install_root": "/home/kevinh/.steam/debian-installation/",
        "game_id": game_id
    }
    return info


async def main():
    print('Simulating decky loader for testing...')
    p = Plugin()
    await p.set_account_id(49847735)
    # print(f'Initial saveinfos { await p.get_saveinfos() }')
    p.ignore_unchanged = False  # Force backup for testing

    # si = await p.do_backup(make_game_info(264710))
    #print(f'Subnautica backup results: { si }')
    #assert si is not None

    si = await p.do_backup(make_game_info(892970))
    print(f'Valheim backup results: { si }')
    assert si is not None

    p.ignore_unchanged = True  # following backup should be skipped because no changes
    si = await p.do_backup(make_game_info(892970))
    assert si is None

    # Test a game that should not exist
    si = await p.do_backup(make_game_info(555))
    assert si is None

    # Test a game with unsupported vdf (raft)
    si = await p.do_backup(make_game_info(648800))
    assert si is None

    infos = await p.get_saveinfos()
    saves = list(filter(lambda i: not i["is_undo"], infos))
    print(f'Current saveinfos { infos }')

    # Try to restore from our most recently created valheim snapshot
    i = saves[0]
    p.dry_run = True  # Don't accidentally toast my running game
    await p.do_restore(i)

    print('Tests complete')

asyncio.run(main())
