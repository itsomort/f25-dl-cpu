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
        if type(o) == int and (o > 255 or o < -128):
            raise ValueError("Immediate is not in correct range (-128 to 127) or (0 to 255)")
    
    def _validate_val(self):
        # modulo handles overflow and underflow case
        self._value %= 256

    def get_val(self):
        return self._value
        
    
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
        
        self.opidx = index
        self._operation = operation
        tokens.pop(0) # remove operation

        if 0 <= index <= 5 and len(tokens) != 2:
            raise ValueError(f"Incorrect number of arguments for {operation}: requires 2, {len(tokens)} were given")
        elif 6 <= index <= 13 and len(tokens) != 1:
            raise ValueError(f"Incorrect number of arguments for {operation}: requires 1, {len(tokens)} were given")
        elif 14 <= index <= 20 and len(tokens) != 3:
            raise ValueError(f"Incorrect number of arguments for {operation}: requires 3, {len(tokens)} were given")
        
        # correct number of arguments, now set list
        self.args = tokens

    def __str__(self):
        return f"{self._operation} ({self.opidx}) {list(token for token in self.args)}"
    
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

        self._regmap = {"A": self._A, "B": self._B, "C": self._C,
                        "D": self._D, "X": self._X, "Y": self._Y }

        # create flags
        self._zerof = False
        self._negativef = False 

    def __str__(self):
        lines = []
        lines.append("REGISTERS: ")
        for key, value in self._regmap.items():
            lines.append(f"Register {key}: {hex(value.get_val())}")
        lines.append("\nFLAGS")
        lines.append(f"Zero Flag: {'1' if self._zerof else '0'}")
        lines.append(f"Negative Flag: {'1' if self._negativef else '0'}\n")
        lines.append(f"PROGRAM COUNTER: {self._index}")
        if(self._index >= len(self._program)):
            lines.append("EXECUTION OVER")
        else:
            lines.append(f"CURRENT INSTRUCTION: {str(self._program[self._index])}")

        return "\n".join(lines)
        
    def _set_flags(self, val):
        if val == 0:
            self._zerof = True
        else:
            self._zerof = False

        if val < 0:
            self._negativef = True
        else:
            self._negativef = False

    # either 1 byte or 2 byte register
    def _immediate(self, imm, size):
        val = None
        # let python handle errors for non-numbers
        if imm.find("x") != -1: # hexadecimal
            val = int(imm, 16)
        elif imm.find("b") != -1: # binary
            val = int(imm, 2)
        else: # decimal
            val = int(imm, 10)

        if size == 1 and not (-128 <= val <= 255):
            raise ValueError("Immediate out of range for 1 byte register")
        if size == 2 and not (0 <= val <= 65535):
            raise ValueError("Immediate out of range for 2 byte register")

    def step(self):
        regs1b = ["A", "B", "C", "D"]
        regs2b = ["X", "Y"]

        # this will step through 1 instruction and update everything accordingly
        # first, determine what instruction we're executing
        if(self._index >= len(self._program)):
            raise EOFError("Execution of program ended")
        
        inst = self._program[self._index]
        inc_pc = True # whether to increment program counter
        # next, based on index, execute instruction and update flags

        match inst.opidx:
            case 0: # MOV
                dest = inst.args[0]
                src = inst.args[1]
                # check that registers are A, B, C, D, X, Y
                if dest not in regs1b and dest not in regs2b:
                    raise ValueError("Destination register not A, B, C, D, X, or Y")
                if src not in regs1b and src not in regs2b:
                    raise ValueError("Source register not A, B, C, D, X, or Y")
                
                # check if register sizes are the same
                if (dest in regs1b and src in regs2b) or (dest in regs2b and src in regs1b):
                    raise ValueError("Incompatible register sizes for MOV")
                
                # transfer data:
                # load the destination register with the value of the source register
                self._regmap[dest].load(self._regmap[src].get_val())
                
            case 1: # LDI
                dest = inst.args[0]
                if dest not in regs1b and dest not in regs2b:
                    raise ValueError("Destination register not A, B, C, D, X, or Y")
            
                if dest in regs1b:
                    imm = self._immediate(inst.args[1], 1)
                else:
                    imm = self._immediate(inst.args[1], 2)

                # load destination register with value
                self._regmap[dest].load(imm)

            case 2: # RDM
                dest = inst.args[0]
                src = inst.args[1]
                if dest not in regs1b:
                    raise ValueError("Destination register not A, B, C, D")
                if src not in regs2b:
                    raise ValueError("Source register for address not X, Y")
                
                # get value contained in X or Y
                addr = self._regmap[src].get_val()
                # grab corresponding value from memory and load into register
                self._regmap[dest].load(self._memory[addr])
                
            case 3: # WRM
                dest = inst.args[0]
                src = inst.args[1]
                if dest not in regs2b:
                    raise ValueError("Destination register for address not X, Y")
                if src not in regs1b:
                    raise ValueError("Source register not A, B, C, D")
                
                # get address for data
                addr = self._regmap[dest].get_val()
                # and change memory to data from src register
                self._memory[addr] = self._regmap[src].get_val()
            
            case 4: # CMP
                r1 = inst.args[0]
                r2 = inst.args[1]
                # perform comparison and save value
                val = r1.cmp(r2)
                # set corresponding flags
                self._set_flags(val)


            case 5: # CMPI
                r1 = inst.args[0]
                imm = self._immediate(inst.args[1], 1)

                # same as regular CMP
                val = r1.cmp(imm)
                self._set_flags(val)

            case 6: # JMP
                # get index of specified label and jump
                label = inst.args[0]
                self._index = self._labels[label]
                inc_pc = False
            case 7: # JNZ
                # jump if zero flag is false
                label = inst.args[0]
                if not self._zerof:
                    self._index = self._labels[label]
                    inc_pc = False
                
            case 8: # JEZ
                # jump if zero flag is true
                label = inst.args[0]
                if self._zerof:
                    self._index = self._labels[label]
                    inc_pc = False
                
            case 9: # JNE
                # jump if negative flag is true
                label = inst.args[0]
                if self._negativef:
                    self._index = self._labels[label]
                    inc_pc = False
                
            case 10: # JPZ
                # jump if negative flag is false
                label = inst.args[0]
                if not self._negativef:
                    self._index = self._labels[label]
                    inc_pc = False
                
            case 11: # INC
                reg = inst.args[0]
                if reg not in regs2b:
                    raise ValueError("Register to increment is not X or Y")
                self._regmap[reg].increment()

            case 12: # DEC
                reg = inst.args[0]
                if reg not in regs2b:
                    raise ValueError("Register to decrement is not X or Y")
                self._regmap[reg].decrement()

            case 13: # INV
                reg = inst.args[0]
                if reg not in regs1b:
                    raise ValueError("Register to invert is not A, B, C, or D")
                self._regmap[reg].inv()

            case 14: # ADD
                dest = inst.args[0]
                r1 = inst.args[1]
                r2 = inst.args[2]

                if dest not in regs1b:
                    raise ValueError("Destination register is not A, B, C, or D")
                if r1 not in regs1b:
                    raise ValueError("First argument is not A, B, C, or D")
                if r2 not in regs1b:
                    raise ValueError("Second argument is not in A, B, C or D")
                
                # get values
                arg1 = self._regmap[r1].get_val()
                arg2 = self._regmap[r2].get_val()

                # for overflow
                s = (arg1 + arg2) % 256
                # load into register
                val = self._regmap[dest].load(s)

                # set flags
                self._set_flags(val)

            case 15: # ADDI
                dest = inst.args[0]
                r1 = inst.args[1]
                imm = inst.args[2]

                if dest not in regs1b:
                    raise ValueError("Destination register is not A, B, C, or D")
                if r1 not in regs1b:
                    raise ValueError("First argument is not A, B, C, or D")
                
                arg1 = self._regmap[r1].get_val()
                arg2 = self._immediate(imm, 1)

                s = (arg1 + arg2) % 256
                val = self._regmap[dest].load(s)

                self._set_flags(val)

            case 16: # SUB
                dest = inst.args[0]
                r1 = inst.args[1]
                r2 = inst.args[2]

                if dest not in regs1b:
                    raise ValueError("Destination register is not A, B, C, or D")
                if r1 not in regs1b:
                    raise ValueError("First argument is not A, B, C, or D")
                if r2 not in regs1b:
                    raise ValueError("Second argument is not in A, B, C or D")
                
                arg1 = self._regmap[r1].get_val()
                arg2 = self._regmap[r2].get_val()

                s = (arg1 - arg2) % 256
                val = self._regmap[dest].load(s)

                self._set_flags(val)

            case 17: # SUBI
                dest = inst.args[0]
                r1 = inst.args[1]
                imm = inst.args[2]

                if dest not in regs1b:
                    raise ValueError("Destination register is not A, B, C, or D")
                if r1 not in regs1b:
                    raise ValueError("First argument is not A, B, C, or D")
                
                arg1 = self._regmap[r1].get_val()
                arg2 = self._immediate(imm, 1)

                s = (arg1 - arg2) % 256
                val = self._regmap[dest].load(s)

                self._set_flags(val)

            case 18: # ORL
                dest = inst.args[0]
                r1 = inst.args[1]
                r2 = inst.args[2]

                if dest not in regs1b:
                    raise ValueError("Destination register is not A, B, C, or D")
                if r1 not in regs1b:
                    raise ValueError("First argument is not A, B, C, or D")
                if r2 not in regs1b:
                    raise ValueError("Second argument is not in A, B, C or D")
                
                arg1 = self._regmap[r1].get_val()
                arg2 = self._regmap[r2].get_val()
            case 19: # ANDL
                pass
            case 20: # XORL
                pass
            case _:
                raise ValueError("Unknown instruction index")
        
        if inc_pc:
            self._index += 1
        