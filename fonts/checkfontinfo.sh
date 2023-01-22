#!/bin/bash

# Specify the directory containing the font files
directory="./"

# Change to the specified directory
cd "$directory"

# Loop through all the otf and ttf files in the directory
for file in *.otf *.ttf; do
    # Run the command with the current file as an argument
    python3 checkfontinfo_prod.py "$file"
done
