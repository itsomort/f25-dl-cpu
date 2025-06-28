from enum import Enum

class Opcode(Enum):
    # Data management
    MOV = 0
    LDI = 1
    RDM = 2
    WRM = 3

    # Branching
    JMP = 4
    JNZ = 5
    JEZ = 6
    JNE = 7
    JPZ = 8

    # Logic/Arithmetic
    ADD = 9
    ADDI = 10
    SUB = 11
    SUBI = 12
    INC = 13
    DEC = 14
    ORL = 15
    ANDL = 16
    XORL = 17
    INV = 18
    CMP = 19

