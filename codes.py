from __future__ import annotations
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

# 1 byte register for A, B, C, D
class Register1B():
    # create a 1 byte register
    def __init__(self, name):
        # should only contain values 0 - 255
        self._value = 0
        #self._name = A, B, C, D
        self._name = name

    def __str__(self):
        return f"Register {self._name}: {hex(self._value)}"
    
    def _arg_check(self, o):
        # check if value is an immediate or a register
        if not isinstance(o, (int, Register1B)):
            raise TypeError("Argument is not an integer or Register1B")
        # check if immediate is in proper range
        if type(o) == int and (o > 255 or o < -127):
            raise ValueError("Immediate is not in correct range (-127 to 128) or (0 to 255)")
    
    def _validate_val(self):
        # modulo handles overflow and underflow case
        self._value %= 256
        
    
    def load(self, o):
        self._arg_check(o)
        
        if isinstance(o, int):
            self._value = o
        elif isinstance(o, Register1B):
            self._value = o._value

        self._validate_val()

    # addition
    def add(self, o):
        self._arg_check(o)
        # add values depending on type

        if isinstance(o, int):
            self._value += o
        elif isinstance(o, Register1B):
            self._value += o._value
        
        self._validate_val()
        return self._value

    # subtraction
    def sub(self, o):
        self._arg_check(o)
        
        # subtract value depending on type
        if isinstance(o, int):
            self._value -= o
        elif isinstance(o, Register1B):
            self._value -= o._value
        
        self._validate_val()
        return self._value

    # logical OR
    def orl(self, o):
        self._arg_check(o)

        if isinstance(o, int):
            self._value |= o
        elif isinstance(o, Register1B):
            self._value |= o._value

        self._validate_val()
        return self._value

    # logical AND
    def andl(self, o):
        self._arg_check(o)

        if isinstance(o, int):
            self._value &= o
        elif isinstance(o, Register1B):
            self._value &= o._value

        self._validate_val()
        return self._value

    def xorl(self, o):
        self._arg_check(o)

        if isinstance(o, int):
            self._value ^= o
        elif isinstance(o, Register1B):
            self._value ^= o._value

        self._validate_val()
        return self._value

    def inv(self):
        # bitwise not in python (~) is stupid
        # so we do something else to make it work

        self._value = 255 - self._value
        self._validate_val()
        return self._value

    # compare is a bit different
    # returns 0 if self._value = o
    # returns 1 if self._value > o
    # returns -1 if self._value < o

    def cmp(self, o):
        self._arg_check(o)

        cmp_val = 0
        if isinstance(o, int):
            cmp_val = o
        elif isinstance(o, Register1B):
            cmp_val = o._value

        if(self._value == cmp_val):
            return 0
        elif(self._value > cmp_val):
            return 1
        else:
            return -1
        
# class Instruction():
    # take in string, make opcode and register targets


