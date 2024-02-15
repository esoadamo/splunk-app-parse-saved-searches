#!/usr/bin/env python3

"""
Increases minor app version by 1 in all relevant places
"""

from pathlib import Path
from json import loads

DIR_APP = Path(__file__) / ".." /  ".." / "security_saved_searches"
FILE_MANIFEST = DIR_APP / "app.manifest"
FILE_CONF = DIR_APP / "default" / "app.conf"
FILE_POERTY = DIR_APP / ".." / "pyproject.toml"

with FILE_MANIFEST.open('r') as f:
    manifest = f.read()

with FILE_CONF.open('r') as f:
    conf = f.read()
    
with FILE_POERTY.open('r') as f:
    poetry = f.read()

version = loads(manifest)["info"]["id"]["version"]
version_stable, version_minor = version.rsplit(".", 1)

version_minor = int(version_minor)
version_minor += 1

version_new = f"{version_stable}.{version_minor}"

manifest = manifest.replace(version, version_new)
conf = conf.replace(version, version_new)
poetry = poetry.replace(version, version_new)

with FILE_MANIFEST.open('w') as f:
    f.write(manifest)
    
with FILE_CONF.open('w') as f:
    f.write(conf)

with FILE_POERTY.open('w') as f:
    f.write(poetry)
