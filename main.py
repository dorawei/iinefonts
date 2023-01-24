import csv
import json
from fontTools import ttLib
from fontTools.ttLib import TTFont
import os
import subprocess
from os.path import join
import ast

def generate_css(font_name, slice_id, unicode_ranges, lang, css_code_complete):
    css_template = """/* {slice_id} */
@font-face {{
  font-family: '{font_name}';
  font-style: normal;
  font-weight: 400;
  src: url(https://webfonts.iine.ink/output_files/{font_name}/{font_name}_{lang}_{slice_id}.woff2) format('woff2');
  unicode-range: {unicode_ranges};
}}\n"""
    css_code = css_template.format(font_name=font_name, slice_id=slice_id, unicode_ranges=unicode_ranges, lang=lang)
    css_file = f'output_files/{font_name}/{font_name}_{lang}.css'
    css_code_complete = css_code_complete + css_code
    # check if the file exists
    if os.path.exists(css_file):
        # if the file exists, wipe the old content and save the new content
        with open(css_file, 'w') as f:
            f.write(css_code_complete)
    else:
        # if the file does not exist, create it and save the content
        os.makedirs(os.path.dirname(css_file), exist_ok=True)
        with open(css_file, 'w') as f:
            f.write(css_code_complete)
    return css_code_complete


def convert_to_unicode_ranges(string):
    # Initialize empty list to store unicode ranges
    unicode_ranges = []
    # Iterate over each character in the string
    for char in string:
        # Get the unicode code point of the character
        code_point = ord(char)
        # If the code point is in the ASCII range, add it to the list as is
        if code_point < 128:
            unicode_ranges.append(f"U+{code_point:04X}")
        # If the code point is outside the ASCII range, add it to the list as a range
        else:
            unicode_ranges.append(f"U+{code_point:04X}-{code_point:04X}")
    # Join the list of unicode ranges into a single string
    return ",".join(unicode_ranges)
    

def generate_subsetted_font(font_file, unicode_ranges, font_name, slice_id, lang):
    """
    Generates subsetted font file using pyftsubset
    """
    # create a folder for the font
    os.makedirs(join("output_files", font_name), exist_ok=True)
    output_file = join("output_files", font_name, f"{font_name}_{lang}_{slice_id}.woff2")
    # Set the command and arguments
    command = "pyftsubset"
    arguments = [
        f"{font_file}",
        f"--unicodes={unicode_ranges}",
        "--layout-features=*",
        "--flavor=woff2",
        f"--output-file={output_file}"
    ]

    # Execute the command
    subprocess.run([command, *arguments])

def generate_slices(char_list, max_chars_per_slice):
    """
    Generates slice IDs and sliced characters based on character frequency order
    """
    # Determine the number of slices needed
    num_slices = len(char_list) // max_chars_per_slice
    if len(char_list) % max_chars_per_slice != 0:
        num_slices += 1

    # Create a list to hold the sliced characters
    slices = []
    for i in range(num_slices):
        start = i * max_chars_per_slice
        end = (i + 1) * max_chars_per_slice
        slices.append(char_list[start:end])

    # Reverse the slices so the most frequent slice is at the end
    slices.reverse()
    
    return slices

def generate_woff(font_file, slices_dict, font_name):
    """
    Generates WOFF subsets of the font
    """
    font = ttLib.TTFont(font_file)

    for slice_id, slice_chars in slices_dict.items():
        subset = font.getSubset(slice_chars)
        subset.save(f"{font_name}_slice_{slice_id}.woff")

    font.close()

def main():
    # Load Google frequency list
    google_freq = {}
    for lang in ['zh-HK', 'zh-TW', 'zh-CN', 'ja']:
        with open(f'google_freq_{lang}.csv') as f:
            google_freq[lang] = [char for char in f.read().split()]


    # Read fonts_info.csv file
    with open('fonts/fonts_info.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            font_name, font_file, langs = row
            langs = ast.literal_eval(langs)
            # Open font file
            font = TTFont(font_file)
            unicode_mapping = font.getBestCmap()
            codepoints = list(unicode_mapping.keys())
            font_chars = []
            for codepoint in codepoints:
                character = chr(codepoint)
                font_chars.append(character)
            font.close()

            # Get final character list for each language
            final_char_list = {}
            for lang in langs:
                print(f'Subsetting {font_name} {lang}...')
                css_code_complete = ""
                final_char_list = {'google': [], 'supp': []}
                for char in google_freq[lang]:
                    if char in font_chars:
                        final_char_list['google'].append(char)
                for char in font_chars:
                    if char not in final_char_list['google']:
                        final_char_list['supp'].append(char)


                # Generate slices
                slices_dict = {}
                if final_char_list['google']:
                    slices = generate_slices(final_char_list['google'], 600)
                    num_slices = len(slices)
                    slice_ids = []
                    for i in range(num_slices):
                        slice_ids.append(f'google_{i}')
                    slices_dict['google'] = {}
                    for i in range(num_slices):
                        slices_dict['google'][slice_ids[i]] = slices[i]
                    #slices_dict['google'] = generate_slices(final_char_list['google'], 600)
                if final_char_list['supp']:
                    slices = generate_slices(final_char_list['supp'], 600)
                    num_slices = len(slices)
                    slice_ids = []
                    for i in range(num_slices):
                        slice_ids.append(f'supp_{i}')
                    slices_dict['supp'] = {}
                    #for i in range(num_slices):
                        #slices_dict['supp'][slice_ids[i]] = slices[i]
                        #removed supp slices for now, to reduce css file size [temp workaround]

                # Generate subsetted font files
                for slice_type, slices in slices_dict.items():
                    for slice_id, slice_chars in slices.items():
                        unicode_ranges = convert_to_unicode_ranges(slice_chars)
                        generate_subsetted_font(font_file, unicode_ranges, font_name, slice_id, lang)
                        css_code_complete = generate_css(font_name, slice_id, unicode_ranges, lang, css_code_complete)


    print("Subsetting Done!")

if __name__ == "__main__":
    main()
