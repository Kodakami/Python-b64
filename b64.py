# b64.py

# A base-64 encoding and decoding module.

import sys
from collections import namedtuple
from bit_converter import BitConverter

# A block of relevant UTF-8 characters and how long the block is.
B64CharBlock = namedtuple("B64CharBlock", "utf8_starting_index span")

# constants
UPPER_CASE = B64CharBlock(utf8StartingIndex=65, span=26)    # A...Z
LOWER_CASE = B64CharBlock(utf8StartingIndex=97, span=26)    # a...z
NUMBERS = B64CharBlock(utf8StartingIndex=48, span=10)       # 0...9
CHAR_62 = B64CharBlock(utf8StartingIndex=43, span=1)        # +
CHAR_63 = B64CharBlock(utf8StartingIndex=47, span=1)        # /
PADDING_CHAR = '='

# Base-64 starts on upper-case, then lower-case, then numbers, then the last two which vary by implementation.
char_blocks = [UPPER_CASE, LOWER_CASE, NUMBERS, CHAR_62, CHAR_63]

def __get_b64_char(int_value:int):
    # If the value is representable by base-64,
    if (int_value in range(0, 64)):
        working_value = int_value
        
        # For each type of character in b64...
        for block in char_blocks:
            # If it's within the block,
            if working_value < block.span:
                # Return the corresponding character.
                return chr(block.utf8_starting_index + working_value)
            else:
                # Otherwise, remove the number of characters in this block from the byte value (queue up for next block).
                working_value -= block.span
    
    raise Exception("Argument out of range.")

def __get_int_value(b64_char:str):
    int_value = 0

    code_point = ord(b64_char[0])
    for block in char_blocks:
        if code_point in range(block.utf8_starting_index, block.utf8_starting_index + block.span):
            return int_value + code_point - block.utf8_starting_index
        else:
            int_value += block.span
    return -1

# Convert a list of octet byte values to a base-64 string.
def to_b64(bytes:bytes):
    # Convert octets to sextets.
    bc = BitConverter(8, 6)
    
    sextets, padding_count = bc.convert(bytes)
    chars = []
    
    # Main sequence.
    for sextet in sextets:
        chars.append(__get_b64_char(sextet))
    
    # Padding characters, if needed.
    chars.extend(PADDING_CHAR * (padding_count // 2))

    return ''.join(chars)

# Convert a base-64 string to a list of octet byte values.
def to_bytes(b64:str):
    # Convert sextets to octets.
    bc = BitConverter(6, 8)

    sextets = []
    for c in b64:
        if c == PADDING_CHAR:
            break
        sextets.append(__get_int_value(c))

    octets, paddingCount = bc.convert(sextets)

    # If there were any padding bits,
    if paddingCount > 0:
        # Discard the final character.
        del octets[len(octets) - 1]

    return octets
    
# Expected console command format: python b64.py encode "Encode this phrase."
# Expected console command format: python b64.py decode RW5jb2RlIHRoaXMgcGhyYXNlLg==
def __console_program():
    # console arg 0 is the script name
    # console arg 1 is the encode/decode flag
    encode = sys.argv[1] == "encode"
    
    if encode:
        argUtf8 = sys.argv[2].strip('\"')
        print("UTF-8:", argUtf8)

        octets = bytearray()
        for c in argUtf8:
            octets.append(ord(c))

        print("Base-64:", to_b64(bytes(octets)))
    else:
        argB64 = sys.argv[2]
        print("Base-64:", argB64)

        chars = []
        for c in to_bytes(argB64):
            chars.append(chr(c))

        print("UTF-8: " + '\"' + ''.join(chars) + '\"')

__console_program()