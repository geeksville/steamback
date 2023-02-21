import logging
import shutil

logging.basicConfig(filename="/tmp/deckshot.log",
                    format='[Deckshot] %(asctime)s %(levelname)s %(message)s',
                    filemode='w+',
                    force=True)
logger=logging.getLogger()

# logger.setLevel(logging.INFO) # can be changed to logging.DEBUG for debugging issues
# can be changed to logging.DEBUG for debugging issues

logger.setLevel(logging.DEBUG)

class Plugin:
    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    async def add(self, left, right):
        return left + right

    async def set_account_id(self, idnum):
        return "FIXME"

    """
    Backup a particular game.

    Returns a new SaveInfo object or null if no backup was needed or possible
    """
    async def do_backup(self, gameIdNum):
        return "FIXME"

    """
    Restore a particular savegame using the saveinfo object
    """
    async def do_restore(self, saveinfo):
        pass

    """
    Return all available saves, newest save first and undo as the absolute first

    Returns an array of SaveInfo objects
    """
    async def get_saveinfos(self):
        return [ "fish" ]

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        logger.info("Deckshot running!")
    
    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        logger.info("Deckshot exiting!")

