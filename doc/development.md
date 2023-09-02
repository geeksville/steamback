# Developer instructions for Steamback

This document is a collection of instructions for developers of Steamback.

## Directory structure:

* /src is the Steam Deck plugin Javascript
* /py_modules/steamback is the core python module that provides the syncing/steam engine
* main.py is only used in the Steam Deck case as glue between the module and the Decky Loader

## Formatting

Please use the official PEP8 python formatting conventions for all python code.  If you are using the recommended VS-Code editor, this will be the default formatter for python.

## We love pull requests, but...

Please send in pull-requests with improvements you make.  We'd love to merge them.  

One caveat: please make the requests 'clean' in the sense that they only fix/improve one thing per PR and they don't include reformatting on areas of code you haven't intended to change.

Because when a PR comes in that fixes many different things and also reformats a bunch of code it is almost impossible to review (to check for unintended changes).

## Using this module in other projects

The python "steamback" module can be used in your other python projects.  See the (crude) developer documentation [here](steamback/index.html).

## Releasing new builds to pypi

The desktop app is distributed via pip.  To make a new release (if you are one of the developers with release keys):

```
# make sure build tools are up-to-date
sudo apt install python3.10-venv
python3 -m pip install --upgrade build

# do the build
python3 -m build
```

## If you are developing for Steam Deck (Decky Loader)

Good tips [here](https://wiki.deckbrew.xyz/en/plugin-dev/cef-debugging).