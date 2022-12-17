# b64.py

# A base-64 encoding and decoding module.

import sys
from collections import namedtuple
from bit_converter import BitConverter

# a block of relevant utf-8 characters and how long the block is
b64CharBlock = namedtuple("b64CharBlock", "utf8StartingIndex span")

# constants
UPPER_CASE = b64CharBlock(utf8StartingIndex=65, span=26)    # A...Z
LOWER_CASE = b64CharBlock(utf8StartingIndex=97, span=26)    # a...z
NUMBERS = b64CharBlock(utf8StartingIndex=48, span=10)       # 0...9
CHAR_62 = b64CharBlock(utf8StartingIndex=43, span=1)        # +
CHAR_63 = b64CharBlock(utf8StartingIndex=47, span=1)        # /
PADDING_CHAR = '='

# base-64 starts on upper-case, then lower-case, then numbers, then the last two which vary by implementation
charBlocks = [UPPER_CASE, LOWER_CASE, NUMBERS, CHAR_62, CHAR_63]

def __getB64Char(value:int):
    # if the value is representable by base-64,
    if (value in range(0, 64)):
        workingValue = value
        
        # for each type of character in b64...
        for block in charBlocks:
            # if it's within the block,
            if workingValue < block.span:
                # return the corresponding character
                return chr(block.utf8StartingIndex + workingValue)
            else:
                # otherwise, remove the number of characters in this block from the byte value (queue up for next block)
                workingValue -= block.span
    
    # return an error character if the input was bad
    return '*'

def __getValue(b64Char:str):
    byteValue = 0

    unicodeCodePoint = ord(b64Char[0])
    for block in charBlocks:
        if unicodeCodePoint in range(block.utf8StartingIndex, block.utf8StartingIndex + block.span):
            return byteValue + unicodeCodePoint - block.utf8StartingIndex
        else:
            byteValue += block.span
    return -1

def toB64(bytes:bytes):
    bc = BitConverter(8, 6)
    
    sextets, paddingCount = bc.convert(bytes)
    output = []
    
    # main sequence
    for sextet in sextets:
        output.append(__getB64Char(sextet))
    
    # padding characters, if needed
    output.extend(PADDING_CHAR * (paddingCount // 2))

    return output

def toBytes(b64:str):
    bc = BitConverter(6, 8)

    sextets = []
    for c in b64:
        if c == PADDING_CHAR:
            break
        sextets.append(__getValue(c))

    octets, paddingCount = bc.convert(sextets)

    if paddingCount > 0:
        del octets[len(octets) - 1]

    return octets
    
# expected console command format: python b64.py encode "Encode this phrase."
# expected console command format: python b64.py decode RW5jb2RlIHRoaXMgcGhyYXNlLg==
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

        print("Base-64:", ''.join(toB64(bytes(octets))))
    else:
        argB64 = sys.argv[2]
        print("Base-64:", argB64)

        chars = []
        for c in toBytes(argB64):
            chars.append(chr(c))

        print("UTF-8: " + '\"' + ''.join(chars) + '\"')

__console_program()