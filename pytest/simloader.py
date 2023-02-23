import sys
sys.path.append('..')
sys.path.append('../../decky-loader/plugin')

import asyncio
from main import *

async def main():
    print('Simulating decky loader for testing...')
    p = Plugin()
    await p.set_account_id(49847735)
    # print(f'Initial saveinfos { await p.get_saveinfos() }')
    p.ignore_unchanged = False # Force backup for testing
    si = await p.do_backup(892970)
    print(f'Valheim backup results: { si }')
    assert si is not None

    p.ignore_unchanged = True  # following backup should be skipped because no changes
    si = await p.do_backup(892970)
    assert si is None
    
    # Test a game that should not exist
    si = await p.do_backup(555)
    assert si is None

    # Test a game with unsupported vdf (raft)
    si = await p.do_backup(648800)
    assert si is None

    infos = await p.get_saveinfos()
    saves = list(filter(lambda i: not i["is_undo"], infos))
    print(f'Current saveinfos { infos }')

    # Try to restore from our most recently created valheim snapshot
    i = saves[0]
    p.dry_run = True # Don't accidentally toast my running game
    await p.do_restore(i)

    print('Tests complete')

asyncio.run(main())
