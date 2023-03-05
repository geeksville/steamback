# Desktop version of Steamback

Steamback originally started as a Decky plugin for Steam Decks.  But a number of folks on reddit asked if it could also work on desktop.

![Steamback desktop](desktop-screenshot.png)

## Supported platforms

This is a version Steamback that will hopefully work on Linux, Windows and OS-X.  However the developers have (thus-far) only tested on Linux.  If you try it on Windows or OS-X please send us a note and let us know how it goes.

If you are a developer and find it doesn't work on Windows or OS-X it is probably pretty easy to fix.  We'd love to work with you on a pull-request - please contact us.

## Installing

Steamback is written in python and you should be able to install it by using the standard "pip" python tool with the following command:

```
pip3 install steamback
```

## Using

Run "steamback" to launch the app (currently we don't install platform app icons).

You should launch Steamback any time you are playing Steam games.  It will watch for game exit and take a save-game snapshot (if it can - it is subject to the same limits as the Steam Deck version of the tool).

On the left side of the window you'll see which games installed on your computer that are supported for automatic save-game snapshots.

If you need to revert to a particular snapshot click on it and then choose "Revert".

