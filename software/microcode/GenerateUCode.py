#!/usr/bin/python3
#
# GenerateUCode.py
#
# This utility generates microcode (uCode) for the i281 processor.
# Using a behavioral function, a row of microcode is generated for
# each unique address.
#
# Multiple ROM images may be generated depending on the length of
# the output word.

# Number of address lines on the ROMs
inputSize = 16

# Number of ROMs in the design
romCount = 3

# Number of bits in each ROM, can only do 8 wide for now
romWidth = 8

# Useful constants
# These are specific to i281, and must be changed if the ISA changes
IMEM_BANK = 0
IMEM_WRITE_ENABLE = 1
PROGRAM_COUNTER_MUX = 2
WRITEBACK_ENABLE = 3
PORT_0 = 4
PORT_1 = 6
WRITE_PORT = 8
REGISTERS_WRITE_ENABLE = 10
ALU_SOURCE_MUX = 11
ALU_SELECT = 12
FLAGS_WRITE_ENABLE = 14
ALU_RESULT_MUX = 15
DMEM_INPUT_MUX = 16
DMEM_WRITE_ENABLE = 17
REG_WRITEBACK_MUX = 18

ALU_OP_NOR = 0
ALU_OP_SHIFTR = 1
ALU_OP_ADD = 2
ALU_OP_SUB = 3

ACTIVE_HIGH = 1
ACTIVE_LOW = 0

# Defines the polarity of the assertion signal
# Used to specify if a signal should be active-high or active-low
# Default is active high
def definePolarity(out):
    setPolarity(out, IMEM_BANK, ACTIVE_LOW)
    setPolarity(out, WRITEBACK_ENABLE, ACTIVE_LOW)
    setPolarity(out, REGISTERS_WRITE_ENABLE, ACTIVE_LOW)
    setPolarity(out, FLAGS_WRITE_ENABLE, ACTIVE_LOW)

# Defines the behavior of the microcode
# The inputs to the ROM are place in "inp". This is represented as an
# integer. The "out" array should be modified to match the desired behavior
# of this particular address. It's length is defined by romWidth * romCount
def defineBehavior(inp, out):

    # [15:12] = Unused
    # [11:8] = Flags
    # [7:4] = Opcode
    # [3:0] = Operand

    # Get opcode
    opcode = (inp & 0xF0) >> 4
    
    # Get operand 
    operand = inp & 0x0F
    opA = operand & 0x03
    opB = (operand & 0x0C) >> 2
    
    # Get flags
    flags = (inp & 0xF00) >> 8
    flagZ = (flags & 0b0001)
    flagN = (flags & 0b0010) >> 1
    flagO = (flags & 0b0100) >> 2
    flagC = (flags & 0b1000) >> 3
    
    # Decode instruction
    if opcode == 0x0: # BANK
    
        # Set control paths
        out[IMEM_BANK] = 1
        out[ALU_SOURCE_MUX] = 1
        
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, ALU_SELECT, ALU_OP_ADD)
        return
        
    if opcode == 0x1: # INPUTC / INPUTCF / INPUTD / INPUTDF / CACHE / WRITE
    
        # Get sub-instruction
        if opA == 0: 
            if opB == 0: # INPUTC
                out[IMEM_WRITE_ENABLE] = 1
                out[ALU_RESULT_MUX] = 1
            else: # CACHE
                out[WRITEBACK_ENABLE] = 1
                out[ALU_SOURCE_MUX] = 1
                setPort(out, ALU_SELECT, ALU_OP_ADD)
                setPort(out, PORT_0, opB)
                
            
        if opA == 1: # INPUTCF
            out[IMEM_WRITE_ENABLE] = 1
            out[ALU_SOURCE_MUX] = 1
            setPort(out, ALU_SELECT, ALU_OP_ADD)
        
        if opA == 2:
            if opB == 0: # INPUTD
                out[ALU_RESULT_MUX] = 1
                out[DMEM_INPUT_MUX] = 1
                out[DMEM_WRITE_ENABLE] = 1
            else: # WRITE
                out[IMEM_WRITE_ENABLE] = 1
                out[WRITEBACK_ENABLE] = 1
                out[ALU_SOURCE_MUX] = 1
                setPort(out, ALU_SELECT, ALU_OP_ADD)
                setPort(out, PORT_0, opB)
        
        if opA == 3: # INPUTDF
            out[ALU_SOURCE_MUX] = 1
            setPort(out, ALU_SELECT, ALU_OP_ADD)
            out[DMEM_INPUT_MUX] = 1
            out[DMEM_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_0, opB)
        
        return
        
    if opcode == 0x2: # MOVE
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        out[ALU_SOURCE_MUX] = 1
        setPort(out, ALU_SELECT, ALU_OP_ADD)
    
        # Set ports
        setPort(out, PORT_0, opA)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x3: # LOADI / LOADP
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        out[ALU_RESULT_MUX] = 1
        
        # Set ports
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x4: # ADD
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        setPort(out, ALU_SELECT, ALU_OP_ADD)
        out[FLAGS_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, PORT_1, opA)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x5: # ADDI
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        out[ALU_SOURCE_MUX] = 1
        setPort(out, ALU_SELECT, ALU_OP_ADD)
        out[FLAGS_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x6: # SUB
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        setPort(out, ALU_SELECT, ALU_OP_SUB)
        out[FLAGS_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, PORT_1, opA)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x7: # SUBI
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        out[ALU_SOURCE_MUX] = 1
        setPort(out, ALU_SELECT, ALU_OP_SUB)
        out[FLAGS_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x8: # LOAD
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        out[ALU_RESULT_MUX] = 1
        out[REG_WRITEBACK_MUX] = 1
    
        # Set ports
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0x9: # LOADF
    
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        out[ALU_SOURCE_MUX] = 1
        out[REG_WRITEBACK_MUX] = 1
        setPort(out, ALU_SELECT, ALU_OP_ADD)
    
        # Set ports
        setPort(out, PORT_0, opA)
        setPort(out, WRITE_PORT, opB)
        
        return
        
    if opcode == 0xA: # STORE
    
        # Set control path
        out[ALU_RESULT_MUX] = 1
        out[DMEM_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_1, opB)
        
        return
        
    if opcode == 0xB: # STOREF
    
        # Set control path
        out[ALU_SOURCE_MUX] = 1
        out[DMEM_WRITE_ENABLE] = 1
        setPort(out, ALU_SELECT, ALU_OP_ADD)
    
        # Set ports
        setPort(out, PORT_0, opA)
        setPort(out, PORT_1, opB)
    
        return
        
    if opcode == 0xC: # NORI / SHIFTR
    
        # Set ALU Input
        out[ALU_SOURCE_MUX] = 1
    
        # Get sub-instruction
        if opA == 0: # NORI
            out[REGISTERS_WRITE_ENABLE] = 1
            out[FLAGS_WRITE_ENABLE] = 1
            setPort(out, ALU_SELECT, ALU_OP_NOR)
        
        if opA == 1: # SHIFTR
            out[REGISTERS_WRITE_ENABLE] = 1
            out[FLAGS_WRITE_ENABLE] = 1
            setPort(out, ALU_SELECT, ALU_OP_SHIFTR)
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0xD: # CMP
    
        # Set control path
        out[FLAGS_WRITE_ENABLE] = 1
        setPort(out, ALU_SELECT, ALU_OP_SUB)
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, PORT_1, opA)
    
        return
        
    if opcode == 0xE: # NOR
        
        # Set control path
        out[REGISTERS_WRITE_ENABLE] = 1
        setPort(out, ALU_SELECT, ALU_OP_NOR)
        out[FLAGS_WRITE_ENABLE] = 1
    
        # Set ports
        setPort(out, PORT_0, opB)
        setPort(out, PORT_1, opA)
        setPort(out, WRITE_PORT, opB)
    
        return
        
    if opcode == 0xF: # BRANCH GROUP
    
        # Set ALU result mux
        out[ALU_RESULT_MUX] = 1
    
        # Get sub-instruction
        if operand == 0x0: # BRC (BRAE)
            if flagC == 1:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x1: # BRNC (BRB)
            if flagC == 0:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x2: # BRO
            if flagO == 1:
                out[PROGRAM_COUNTER_MUX] = 1
            
        if operand == 0x3: # BRNO
            if flagO == 0:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x4: # BRN
            if flagN == 1:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x5: # BRNN (BRP)
            if flagN == 0:
                out[PROGRAM_COUNTER_MUX] = 1
               
        if operand == 0x6: # BRE (BRZ)
            if flagZ == 1:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x7: # BRNE (BRNZ)
            if flagZ == 0:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x8: # BRA
            if flagZ == 0 and flagC == 1:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0x9: # BRBE
            if flagZ == 1 or flagC == 0:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0xA: # BRG
            if flagZ == 0 and flagO == flagN:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0xB: # BRGE
            if flagO == flagN:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0xC: # BRL
            if flagO != flagN:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0xD: # BRLE
            if flagZ == 1 or flagO != flagN:
                out[PROGRAM_COUNTER_MUX] = 1
                
        if operand == 0xE: # JUMPR C
            out[ALU_RESULT_MUX] = 0
            out[ALU_SOURCE_MUX] = 1
            out[PROGRAM_COUNTER_MUX] = 1
            setPort(out, ALU_SELECT, ALU_OP_ADD)
            setPort(out, PORT_0, 0x2)
                
        if operand == 0xF: # JUMP
            out[PROGRAM_COUNTER_MUX] = 1
    
        return
    
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
    print("i281 Microcode Generator V0.5")
    print("SD Group 24-14")
    print("Updated Feb 7, 2024")
    
    # Start generating microcode into the array
    print("Generating Behavior Map...")
    ucode = []
    for i in range(2**inputSize):
        # Create output array
        out = [0] * (romCount * romWidth)
        
        # Get the behavior for this address
        defineBehavior(i, out)
        definePolarity(out)
        
        # Add to microcode array
        ucode.append(out)
        
    # Output into multiple image files
    for i in range(romCount):
        print("Writing to ROM-%d.bin" % i)
        bin = open("ROM-%d.bin" % i, "wb")
        
        # Output the specific bytes into the image
        for line in ucode:
            b = 0
        
            for o in range(romWidth):
                b = (b << 1) | line[o + (i * romWidth)]
        
            bin.write(bytes([b]))
            
        bin.close()
    
    print("Operation Complete")

if __name__ == "__main__":
    main()