import asyncio
from main import *

async def main():
    print('Simulating decky loader for testing...')
    p = Plugin()
    await p.set_account_id(49847735)
    print(f'Initial saveinfos { await p.get_saveinfos() }')
    await p.do_backup(892970)
    p.dry_run = True
    # await p.do_restore(892970)
    
    # Test a game that should not exist
    # await p.do_backup(555)
    print(f'Current saveinfos { await p.get_saveinfos() }')
    print('Tests complete')

asyncio.run(main())
