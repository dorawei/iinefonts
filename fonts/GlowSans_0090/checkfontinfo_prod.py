import argparse
import json
from fontTools.ttLib import TTFont

# Parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('font_file', help='The font file to process')
args = parser.parse_args()

print("checking font " + args.font_file + "...")
# Open the font file
font = TTFont(args.font_file)

# Get the font's name table
name_table = font['name']

# Define a dictionary to store the extracted font information
font_info = {}

# Define a dictionary to map name IDs to item names
name_id_map = {
    0: "Copyright",
    1: "Font Family",
    2: "Font Subfamily",
    3: "Unique Identifier",
    4: "Full Name",
    5: "Version",
    6: "Postscript Name",
    7: "Trademark",
    8: "Manufacturer",
    9: "Designer",
    10: "Description",
    11: "URL",
    12: "License Description",
    13: "License Info URL",
    14: "Reserved",
    15: "Typographic Family",
    16: "Typographic Subfamily",
    17: "Compatible Full (Mac only)",
    18: "Sample Text",
    19: "PostScript CID findfont name",
    20: "WWS Family Name",
    21: "WWS Subfamily Name"
}

def get_language_code(platform_id, language_id):
    language_code = ""
    if platform_id == 3: # Microsoft Platform
        if language_id == 0x0409: # en-US
            language_code = "en"
        elif language_id == 0x0411: # ja-JP
            language_code = "ja"
        elif language_id == 0x0804: # zh-CN
            language_code = "zh-CN"
        elif language_id == 0x0c04: # zh-HK
            language_code = "zh-HK"
        elif language_id == 0x0404: #zh-TW
            language_code = "zh-TW"
        else:
            language_code = "unknown"
    elif platform_id == 1: # Macintosh Platform
        # Code to handle Mac languages
        pass
    elif platform_id == 0: # Unicode Platform
        # Code to handle Unicode languages
        pass
    else:
        language_code = "unknown"
    return language_code

# Iterate over all the available name IDs
for name_record in name_table.names:
    name = name_record.toUnicode()
    name_id = name_record.nameID
    platform_id = name_record.platformID
    language_id = name_record.langID
    item_name = name_id_map.get(name_id, "Unknown")

    #get the language code
    language_code = get_language_code(platform_id, language_id)

    # If the language code is not already in the dictionary, add it
    if language_code not in font_info:
        font_info[language_code] = {}

    if item_name not in font_info[language_code]:
        font_info[language_code][item_name] = name

# special handling for Chinese languages
if "zh-HK" not in font_info and "zh-TW" in font_info:
    font_info["zh-HK"] = font_info.pop("zh-TW")


# Get the Unicode mapping
unicode_mapping = font.getBestCmap()

# Get the codepoints
codepoints = list(unicode_mapping.keys())

charlist = []

# Print the characters
for codepoint in codepoints:
    character = chr(codepoint)
    charlist.append(character)

#print(charlist)
# Close the font file
font.close()

GB2312 = "gb2312-han.txt"
BIG5 = "big5-han.txt"
BIG5COMM = "big5-common.txt"
TW1 = "TW-1-4808.txt"
TW2 = "TW-2-6343.txt"
CN1 = "CN-1-3500.txt"
CN2 = "CN-2-7000.txt"
HKSCS = "HKSCS.txt"
HKSUPPCHARA = "suppchara-han.txt"


def check_charset(filename):
    charset = []
    with open(filename, 'r', encoding='UTF-8') as file:
        for line in file:
            charset.append(line.rstrip())
    charset_num = len(charset)
    exist_char_num = sum(char in charset for char in charlist)
    return [exist_char_num, charset_num]
    
def missing_charlist(filename):
    charset = []
    with open(filename, 'r', encoding='UTF-8') as file:
        for line in file:
            charset.append(line.rstrip())
    charset_num = len(charset)
    missing_charlist = [char for char in charset if char not in charlist]
    missing_charnum = len(missing_charlist)
    return [missing_charnum, missing_charlist]

def check_charset_missing_charlist(filename):
    charset = []
    with open(filename, 'r', encoding='UTF-8') as file:
        for line in file:
            charset.append(line.rstrip())
    charset_num = len(charset)
    exist_char_num = sum(char in charset for char in charlist)
    missing_charlist = [char for char in charset if char not in charlist]
    missing_charnum = len(missing_charlist)
    return {"total":charset_num, "exist":exist_char_num, "missing": missing_charnum, "missing_char":missing_charlist}

# Convert the font information to a JSON object
font_info_json = json.dumps(font_info, indent=4, ensure_ascii=False)

# Write the JSON object to a file
jsonfile = args.font_file + ".json"
with open(jsonfile, 'w') as file:
    file.write(font_info_json)