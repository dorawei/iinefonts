#!/bin/bash

for file in *.ttf; do
    python3 -c "from fontTools.ttLib import TTFont; f = TTFont('$file');f.flavor='woff2';f.save('${file%.ttf}.woff2')"
done
