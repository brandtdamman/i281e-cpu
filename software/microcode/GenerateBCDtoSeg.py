#!/usr/bin/python3
#
# GenerateBCDtoSeg.py
#
# This utility generates microcode (uCode) for the i281 processor.
# Using a behavioral function, a row of microcode is generated for
# each unique address.

# Number of address lines on the ROMs
inputSize = 16

# Number of bits in each ROM, can only do 8 wide for now
romWidth = 8

# Useful constants
#           A  B  C  D  E  F  G
SYMBOL_A = [1, 1, 1, 0, 1, 1, 1]
SYMBOL_B = [0, 0, 1, 1, 1, 1, 1]
SYMBOL_C = [1, 0, 0, 1, 1, 1, 0]
SYMBOL_D = [0, 1, 1, 1, 1, 0, 1]
SYMBOL_E = [1, 0, 0, 1, 1, 1, 1]
SYMBOL_F = [1, 0, 0, 0, 1, 1, 1]

#           A  B  C  D  E  F  G
SYMBOL_0 = [1, 1, 1, 1, 1, 1, 0]
SYMBOL_1 = [0, 1, 1, 0, 0, 0, 0]
SYMBOL_2 = [1, 1, 0, 1, 1, 0, 1]
SYMBOL_3 = [1, 1, 1, 1, 0, 0, 1]
SYMBOL_4 = [0, 1, 1, 0, 0, 1, 1]
SYMBOL_5 = [1, 0, 1, 1, 0, 1, 1]
SYMBOL_6 = [1, 0, 1, 1, 1, 1, 1]
SYMBOL_7 = [1, 1, 1, 0, 0, 0, 0]
SYMBOL_8 = [1, 1, 1, 1, 1, 1, 1]
SYMBOL_9 = [1, 1, 1, 1, 0, 1, 1]

ACTIVE_HIGH = 1
ACTIVE_LOW = 0

# Defines the polarity of the assertion signal
# Used to specify if a signal should be active-high or active-low
# Default is active high
def definePolarity(out):
    # setPolarity(out, WRITEBACK_ENABLE, ACTIVE_LOW)
    # setPolarity(out, REGISTERS_WRITE_ENABLE, ACTIVE_LOW)
    # setPolarity(out, FLAGS_WRITE_ENABLE, ACTIVE_LOW)
    return

# Defines the behavior of the microcode
# The inputs to the ROM are place in "inp". This is represented as an
# integer. The "out" array should be modified to match the desired behavior
# of this particular address. It's length is defined by romWidth * romCount
def defineBehavior(inp, out):

    # [14:9] = Unused
    # [8:8] = GAMEMODE
    # [7:7] = Dot (if GAMEMODE)
    # [6:0] = Binary to 7-seg

    seg         = (inp & 0xFF)
    gamemode    = (inp & 0x100) >> 8

    if gamemode == 0x0:
        # map directly
        out[0:7] = [(seg & (2 ** i)) >> i for i in range(8)]

    elif gamemode == 0x1:
        # translate to display
        #? Note: the dot light is ignored without gamemode
        seg = seg & 0xF
        if seg == 0x0:
            out[0:6] = SYMBOL_0
        elif seg == 0x1:
            out[0:6] = SYMBOL_1
        elif seg == 0x2:
            out[0:6] = SYMBOL_2
        elif seg == 0x3:
            out[0:6] = SYMBOL_3
        elif seg == 0x4:
            out[0:6] = SYMBOL_4
        elif seg == 0x5:
            out[0:6] = SYMBOL_5
        elif seg == 0x6:
            out[0:6] = SYMBOL_6
        elif seg == 0x7:
            out[0:6] = SYMBOL_7
        elif seg == 0x8:
            out[0:6] = SYMBOL_8
        elif seg == 0x9:
            out[0:6] = SYMBOL_9
        elif seg == 0xA:
            out[0:6] = SYMBOL_A
        elif seg == 0xB:
            out[0:6] = SYMBOL_B
        elif seg == 0xC:
            out[0:6] = SYMBOL_C
        elif seg == 0xD:
            out[0:6] = SYMBOL_D
        elif seg == 0xE:
            out[0:6] = SYMBOL_E
        elif seg == 0xF:
            out[0:6] = SYMBOL_F

    return

# Sets the polarity of a bit
def setPolarity(out, bit, value):
    if value == ACTIVE_HIGH:
        return

    # Reverse the bits
    if out[bit] == 1:
        out[bit] = 0
        return
    out[bit] = 1

# Sets a port to a 2-bit value
def setPort(out, port, value):
    out[port+1] = value & 0b1
    out[port] = (value>>1) & 0b1


def main():
    print("i281 Microcode Generator V0.1 VIDEOCARD")
    print("SD Group MAY24-14")
    print("Updated Feb 11, 2024")
    print("Author: Gavin Tersteeg and Daryl Damman")

    # Start generating microcode into the array
    print("Generating Behavior Map...")
    ucode = []
    for i in range(2**inputSize):
        # Create output array
        out = [0] * romWidth

        # Get the behavior for this address
        defineBehavior(i, out)
        definePolarity(out)

        # Add to microcode array
        ucode.append(out)

    # Output into image file
    print("Writing to VIDEOROM.bin")
    bin = open("VIDEOROM.bin", "wb")
    bin_inv = open("VIDEOROM_INV.bin", "wb")

    # Output the specific bytes into the image
    for line in ucode:
        b = 0

        for o in range(romWidth):
            b = (b >> 1) | (line[o] << (romWidth-1))

        bin.write(bytes([b]))
        bin_inv.write(bytes([(~b) & 0XFF]))

    bin.close()
    bin_inv.close()

    print("Operation Complete")

if __name__ == "__main__":
    main()