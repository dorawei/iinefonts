#!/bin/bash

for file in *.otf; do
    python3 -c "from fontTools.ttLib import TTFont; f = TTFont('$file');f.flavor='woff2';f.save('${file%.otf}.woff2')"
done
