
import sys
import os
import asyncio
from . import Engine
from .util import make_game_info


async def testImpl(p: Engine):
    print('Simulating decky loader for testing...')

    p.set_account_id(49847735)
    # print(f'Initial saveinfos { await p.get_saveinfos() }')
    p.ignore_unchanged = False  # Force backup for testing

    # Test find_supported
    supported = await p.find_supported(p.all_games)
    print(f'Supported games: ')
    for i in supported:
        print(f'  {i}')

    valheim = make_game_info(p, 892970)
    subnautica = make_game_info(p, 264710)
    subnauticabz = make_game_info(p, 848450)
    mindustry = make_game_info(p, 1127400)
    # shapez = make_game_info(p,1318690)
    timberborn = make_game_info(p, 1062090)
    nms = make_game_info(p, 275850)
    garfield = make_game_info(p, 1085510)

    # Use less .steam/debian-installation/steamapps/appmanifest_848450.acf to find "installdir" property
    # .steam/debian-installation/steamapps/common/SubnauticaZero/SNAppData/SavedGames/

    si = await p.do_backup(garfield)
    print(f'{ garfield } results: { si }')
    assert si is not None

    si = await p.do_backup(nms)
    print(f'no mans sky backup results: { si }')
    assert si is not None

    si = await p.do_backup(timberborn)
    print(f'timberborn backup results: { si }')
    assert si is not None

    # cloud backups seem broken in general for this app
    # si = await p.do_backup(shapez)
    # print(f'shapez backup results: { si }')
    # assert si is not None

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
    si = await p.do_backup(make_game_info(p, 648800))
    assert si is not None

    p.ignore_unchanged = True  # following backup should be skipped because no changes
    si = await p.do_backup(valheim)
    assert si is None

    # Test a game that should not exist
    si = await p.do_backup(make_game_info(p, 555))
    assert si is None

    infos = await p.get_saveinfos()
    saves = list(filter(lambda i: not i["is_undo"], infos))
    print(f'Current saveinfos { infos }')

    # Try to restore from our most recently created valheim snapshot
    i = saves[0]
    p.dry_run = True  # Don't accidentally toast my running game
    await p.do_restore(i)

    print('Tests complete')
