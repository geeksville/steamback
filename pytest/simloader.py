import sys, os, asyncio

sys.path.append(os.path.realpath(".."))
sys.path.append('../../decky-loader/plugin')

from main import *


"""Create a game info object: contains game_id and install_root
"""


def make_game_info(game_id: int, name: str = None) -> dict:
    info = {
        # On a real steamdeck there may be multiple install_roots (main vs sdcard etc) (but only one per game)
        "install_root": "/home/kevinh/.steam/debian-installation/",
        "game_id": game_id,
        "game_name": name
    }
    return info


async def main():
    print('Simulating decky loader for testing...')
    p = Plugin()
    await p.set_account_id(49847735)
    # print(f'Initial saveinfos { await p.get_saveinfos() }')
    p.ignore_unchanged = False  # Force backup for testing

    valheim = make_game_info(892970, "Valheim")
    subnautica = make_game_info(264710, "Subnautica")
    subnauticabz = make_game_info(848450, "Subnautica Below Zero")
    mindustry = make_game_info(1127400)
    # shapez = make_game_info(1318690)
    timberborn = make_game_info(1062090)

    # Use less /home/kevinh/.steam/debian-installation/steamapps/appmanifest_848450.acf to find "installdir" property
    # /home/kevinh/.steam/debian-installation/steamapps/common/SubnauticaZero/SNAppData/SavedGames/

    si = await p.do_backup(timberborn)
    print(f'timberborn backup results: { si }')
    assert si is not None

    # cloud backups seem broken in general for this app
    #si = await p.do_backup(shapez)
    #print(f'shapez backup results: { si }')
    #assert si is not None

    si = await p.do_backup(mindustry)
    print(f'mindustry backup results: { si }')
    assert si is not None

    si = await p.do_backup(subnauticabz)
    print(f'SubnauticaBZ backup results: { si }')
    assert si is not None

    si = await p.do_backup(subnautica)
    print(f'Subnautica backup results: { si }')
    assert si is not None

    si = await p.do_backup(valheim)
    print(f'Valheim backup results: { si }')
    assert si is not None

    # Test a game with formerly unsupported vdf (raft)
    si = await p.do_backup(make_game_info(648800, "Raft"))
    assert si is not None

    p.ignore_unchanged = True  # following backup should be skipped because no changes
    si = await p.do_backup(valheim)
    assert si is None

    # Test a game that should not exist
    si = await p.do_backup(make_game_info(555))
    assert si is None

    # Test find_supported
    candidates = [valheim, subnautica, mindustry]
    supported = await p.find_supported(candidates)
    assert supported == candidates

    infos = await p.get_saveinfos()
    saves = list(filter(lambda i: not i["is_undo"], infos))
    print(f'Current saveinfos { infos }')

    # Try to restore from our most recently created valheim snapshot
    i = saves[0]
    p.dry_run = True  # Don't accidentally toast my running game
    await p.do_restore(i)

    print('Tests complete')

asyncio.run(main())
