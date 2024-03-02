import re
import json
import time
import os
import shutil
import logging
import re
import steamback
from pathlib import Path

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin

logger = decky_plugin.logger


pinstance = None


def get_engine() -> object:
    # we change logging levels late because if done too early it has no effect
    logger.setLevel(logging.DEBUG)

    global pinstance
    if not pinstance:
        app_data_dir = os.environ["DECKY_PLUGIN_RUNTIME_DIR"]
        steam_dir = os.path.join(os.path.expanduser(
            "~"), ".local", "share", "Steam")
        config = steamback.Config(logger, app_data_dir, steam_dir)
        pinstance = steamback.Engine(config)
    return pinstance


class Plugin:

    async def set_account_id(self, id_num: int):
        # logger.info(f'Setting account id { id_num }')
        get_engine().add_account_id(id_num)
        return None  # Must return something to prevent assertion error logspam in JS

    """
    Backup a particular game.

    Returns a new SaveInfo object or None if no backup was needed or possible
    SaveInfo is a dict with filename, game_id, timestamp, is_undo
    game_info is a dict of game_id and install_root
    """
    async def do_backup(self, game_info: dict, dry_run: bool) -> dict:
        return await get_engine().do_backup(game_info, dry_run)

    """
    Restore a particular savegame using the saveinfo object
    """
    async def do_restore(self, save_info: dict):
        return await get_engine().do_restore(save_info)

    """
    Given a list of game_infos, return a list of game_infos which are supported for backups
    """
    async def find_supported(self, game_infos: list) -> list[dict]:
        return await get_engine().find_supported(game_infos)

    """
    Given a list of directory names, return a list of directories that are actually mounted
    """
    async def find_mounted(self, dirs: list) -> list[dict]:
        return await get_engine().find_mounted(dirs)

    """
    Return all available saves, newest save first and undo as the absolute first

    Returns an array of SaveInfo objects
    """
    async def get_saveinfos(self) -> list[dict]:
        return await get_engine().get_saveinfos()

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        logger.info("Steamback running!")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        logger.info("Steamback exiting!")


"""
    This seems busted for me so leaving off for now... -geeksville
    
    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/template.log`
        decky_plugin.migrate_logs(os.path.join(decky_plugin.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
        decky_plugin.migrate_settings(
            os.path.join(decky_plugin.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        decky_plugin.migrate_runtime(
            os.path.join(decky_plugin.DECKY_HOME, "template"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-template"))
"""
