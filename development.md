# Developer instructions for Steamback

This document is a collection of instructions for developers of Steamback.

## Releasing new builds to pypi

The desktop app is distributed via pip.  To make a new release:

```
# make sure build tools are up-to-date
sudo apt install python3.10-venv
python3 -m pip install --upgrade build

# do the build
python3 -m build
```