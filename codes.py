from __future__ import annotations
from enum import Enum

class Opcode(Enum):
    # two argument instructions
    MOV = 0
    LDI = 1
    RDM = 2
    WRM = 3
    CMP = 4
    CMPI = 5

    # one argument instructions
    JMP = 6
    JNZ = 7
    JEZ = 8
    JNE = 9
    JPZ = 10
    INC = 11
    DEC = 12
    INV = 13

    # three argument instructions
    ADD = 14
    ADDI = 15
    SUB = 16
    SUBI = 17
    ORL = 18
    ANDL = 19
    XORL = 20

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

# 2 byte register for X, Y
class Register2B():
    def __init__(self, name):
        # can contain values 0 - 65535
        self._value = 0
        # self._name = X, Y
        self._name = name

    def __str__(self):
        return f"Register {self._name}: {hex(self._value)}"
    
    def _arg_check(self, o):
        if not isinstance(o, int):
            raise TypeError("Argument is not an integer")
        if not (0 <= o <= 65535):
            raise ValueError("Argument out of bounds (0 to 65535)")
        
    def _validate_val(self):
        self._value %= 65535

    def load(self, o):
        self._arg_check(o)
        self._value = o
    
    def increment(self):
        self._value += 1
        self._validate_val()

    def decrement(self):
        self._value -= 1
        self._validate_val()

    def get_val(self):
        return self._value % 1024


# Instruction class
class Instruction():
    def __init__(self, line):
        # line = single instruction
        # first, remove commas and strip whitespace just in case
        if not isinstance(line, str):
            raise TypeError("Instruction is not a string")
        line = line.replace(",", "").strip()
        # then split it by spaces
        tokens = line.split(" ")
        operation = tokens[0]
        index = -1

        for code in (Opcode):
            if(operation == code.name):
                index = code.value
        if index == -1:
            raise ValueError(f"Operation {operation} does not match known list")
        
        self._opidx = index
        self._operation = operation
        tokens.pop(0) # remove operation

        if 0 <= index <= 5 and len(tokens) != 2:
            raise ValueError(f"Incorrect number of arguments for {operation}: requires 2, {len(tokens)} were given")
        elif 6 <= index <= 13 and len(tokens) != 1:
            raise ValueError(f"Incorrect number of arguments for {operation}: requires 1, {len(tokens)} were given")
        elif 14 <= index <= 20 and len(tokens) != 3:
            raise ValueError(f"Incorrect number of arguments for {operation}: requires 3, {len(tokens)} were given")
        
        # correct number of arguments, now set list
        self._args = tokens

    def __str__(self):
        return f"{self._operation} ({self._opidx}) {list(token for token in self._args)}"
    
# main CPU class
class CPU():
    def __init__(self, program, memory, labels):
        # program should be a list of instructions
        if not isinstance(program, list):
            raise TypeError("Given program is not a list")
        
        for inst in program:
            if not isinstance(inst, Instruction):
                raise TypeError("Instruction is not of Instruction type")
        
        self._program = program
        self._index = 0 # index to execute 

        # memory should be prefilled array of numbers with length 1024
        if not isinstance(memory, list):
            raise TypeError("Given memory is not a list")
        
        for val in memory:
            if not isinstance(val, int):
                raise TypeError("Non-numeric value in memory")
        
        if len(memory) != 1024:
            raise ValueError("Length of memory is not 1024")
        
        self._memory = memory

        # labels (for looping) should be a dictionary of strings to integers, or none
        if labels != None and not isinstance(labels, dict):
            raise TypeError("Labels is not None or a dictionary")
        if isinstance(labels, dict):
            for key, value in labels.items():
                if not isinstance(key, str):
                    raise ValueError("Label dictionary has a non-string key")
                if not isinstance(value, int):
                    raise ValueError("Label dictionary has non-integer value")
                
        self._labels = labels

        # create registers
        self._A = Register1B("A")
        self._B = Register1B("B")
        self._C = Register1B("C")
        self._D = Register1B("D")
        self._X = Register2B("X")
        self._Y = Register2B("Y")

        # create flags
        self._zerof = False
        self._negativef = False 

    def step(self):
        regs1b = ["A", "B", "C", "D"]
        regs2b = ["X", "Y"]

        # this will step through 1 instruction and update everything accordingly
        # first, determine what instruction we're executing
        if(self._index >= len(self._program)):
            raise Exception("Execution of program ended")
        
        inst = self._program[self._index]

        # next, based on index, execute instruction and update flags

        match inst.index:
            case 0: # MOV
                pass
            case 1: # LDI
                pass
            case 2: # RDM
                pass
            case 3: # WRM
                pass
            case 4: # CMP
                pass
            case 5: # CMPI
                pass
            case 6: # JMP
                pass
            case 7: # JNZ
                pass
            case 8: # JEZ
                pass
            case 9: # JNE
                pass
            case 10: # JPZ
                pass
            case 11: # INC
                pass
            case 12: # DEC
                pass
            case 13: # INV
                pass
            case 14: # ADD
                pass
            case 15: # ADDI
                pass
            case 16: # SUB
                pass
            case 17: # SUBI
                pass
            case 18: # ORL
                pass
            case 19: # ANDL
                pass
            case 20: # XORL
                pass
            case _:
                raise ValueError("Unknown instruction index")









        
