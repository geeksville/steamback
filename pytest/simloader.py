import asyncio
from main import *

async def main():
    print('Simulating decky loader for testing...')
    p = Plugin()
    await p.set_account_id(49847735)
    # print(f'Initial saveinfos { await p.get_saveinfos() }')
    await p.do_backup(892970)
    
    # Test a game that should not exist
    await p.do_backup(555)

    # Test a game with unsupported vdf (raft)
    await p.do_backup(648800)

    infos = await p.get_saveinfos()
    saves = list(filter(lambda i: not i["is_undo"], infos))
    print(f'Current saveinfos { infos }')

    # Try to restore from our most recently created valheim snapshot
    i = saves[0]
    p.dry_run = True # Don't accidentally toast my running game
    # await p.do_restore(i)

    print('Tests complete')

asyncio.run(main())
