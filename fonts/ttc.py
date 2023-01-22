#!/usr/bin/env python

from fontTools.ttLib.ttCollection import TTCollection
import os
import sys

filename = sys.argv[1]
ttc = TTCollection(filename)
basename = os.path.basename(filename)
for i, font in enumerate(ttc):
    font.save(f"{basename}#{i}.ttf")