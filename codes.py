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
    def add(self, o1, o2):
        self._arg_check(o1)
        self._arg_check(o2)
        # add values depending on type

        if isinstance(o1, Register1B) and isinstance(o2, Register1B):
            self._value = o1.get_val() + o2.get_val()
        # immediates passed in as second argument
        elif isinstance(o1, Register1B) and isinstance(o2, int):
            self._value = o1.get_val() + o2
        else:
            raise TypeError("Bad types for Register1B.add")
        
        self._validate_val()
        return self._value

    # subtraction
    def sub(self, o1, o2):
        self._arg_check(o1)
        self._arg_check(o2)
        
        # subtract value depending on type
        if isinstance(o1, Register1B) and isinstance(o2, Register1B):
            self._value = o1.get_val() - o2.get_val()
        elif isinstance(o1, Register1B) and isinstance(o2, int):
            self._value = o1.get_val() - o2
        else:
            raise TypeError("Bad types for Register1B.sub")
        
        self._validate_val()
        return self._value

    # logical OR
    def orl(self, o1, o2):
        self._arg_check(o1)
        self._arg_check(o2)

        # only registers passed in here
        if isinstance(o1, Register1B) and isinstance(o2, Register1B):
            self._value = o1.get_val() | o2.get_val()
        else:
            raise TypeError("Bad types for Register1B.orl")
        

        self._validate_val()
        return self._value

    # logical AND
    def andl(self, o1, o2):
        self._arg_check(o1)
        self._arg_check(o2)

        if isinstance(o1, Register1B) and isinstance(o2, Register1B):
            self._value = o1.get_val() & o2.get_val()
        else:
            raise TypeError("Bad types for Register1B.andl")

        self._validate_val()
        return self._value

    def xorl(self, o1, o2):
        self._arg_check(o1)
        self._arg_check(o2)

        if isinstance(o1, Register1B) and isinstance(o2, Register1B):
            self._value = o1.get_val() ^ o2.get_val()
        else:
            raise TypeError("Bad types for Register1B.xorl")

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
        operation = tokens[0].upper()
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

    regs1b = ["A", "B", "C", "D"]
    regs2b = ["X", "Y"]

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
            lines.append(f"NEXT INSTRUCTION: {str(self._program[self._index])}\n\n")

        return "\n".join(lines)
        
    def _set_flags(self, val):
        if val == 0:
            self._zerof = True
        else:
            self._zerof = False

        # vals > 127 indicate MSB is 1, so negative
        if val < 127:
            self._negativef = True
        else:
            self._negativef = False

    # either 1 byte or 2 byte register
    def _immediate(self, imm, size):
        # automatic base detection (didnt know this was a thing)
        val = int(imm, 0)

        if size == 1 and not (-128 <= val <= 255):
            raise ValueError("Immediate out of range for 1 byte register")
        if size == 2 and not (0 <= val <= 65535):
            raise ValueError("Immediate out of range for 2 byte register")
        
        return val
    
    def _reg_check2(self, dest, r1):
        if dest not in CPU.regs1b:
            raise ValueError("Destination register is not A, B, C, or D")
        if r1 not in CPU.regs1b:
            raise ValueError("First argument is not A, B, C, or D")

    def _reg_check3(self, dest, r1, r2):
        if dest not in CPU.regs1b:
            raise ValueError("Destination register is not A, B, C, or D")
        if r1 not in CPU.regs1b:
            raise ValueError("First argument is not A, B, C, or D")
        if r2 not in CPU.regs1b:
            raise ValueError("Second argument is not in A, B, C or D")

    def step(self):
        

        # this will step through 1 instruction and update everything accordingly
        # first, determine what instruction we're executing
        if(self._index >= len(self._program)):
            raise EOFError("Execution of program ended")
        
        inst = self._program[self._index]
        inc_pc = True # whether to increment program counter

        # shorthand for commonly used arguments
        dest = inst.args[0]
        reg = inst.args[0]
        src = "" # my ide gets mad if i dont do this
        r1 = ""
        if len(inst.args) > 1:
            src = inst.args[1]
            r1 = inst.args[1]
        r2 = ""
        if len(inst.args) > 2:
            r2 = inst.args[2]

        # next, based on index, execute instruction and update flags
        match inst.opidx:
            case 0: # MOV
                # check that registers are A, B, C, D, X, Y
                if dest not in CPU.regs1b and dest not in CPU.regs2b:
                    raise ValueError("Destination register not A, B, C, D, X, or Y")
                if src not in CPU.regs1b and src not in CPU.regs2b:
                    raise ValueError("Source register not A, B, C, D, X, or Y")
                
                # check if register sizes are the same
                if (dest in CPU.regs1b and src in CPU.regs2b) or (dest in CPU.regs2b and src in CPU.regs1b):
                    raise ValueError("Incompatible register sizes for MOV")
                
                # transfer data:
                # load the destination register with the value of the source register
                self._regmap[dest].load(self._regmap[src].get_val())
                
            case 1: # LDI
                if dest not in CPU.regs1b and dest not in CPU.regs2b:
                    raise ValueError("Destination register not A, B, C, D, X, or Y")
            
                if dest in CPU.regs1b:
                    imm = self._immediate(inst.args[1], 1)
                else:
                    imm = self._immediate(inst.args[1], 2)

                # load destination register with value
                self._regmap[dest].load(imm)

            case 2: # RDM
                if dest not in CPU.regs1b:
                    raise ValueError("Destination register not A, B, C, D")
                if src not in CPU.regs2b:
                    raise ValueError("Source register for address not X, Y")
                
                # get value contained in X or Y
                addr = self._regmap[src].get_val()
                # grab corresponding value from memory and load into register
                self._regmap[dest].load(self._memory[addr])
                
            case 3: # WRM
                if dest not in CPU.regs2b:
                    raise ValueError("Destination register for address not X, Y")
                if src not in CPU.regs1b:
                    raise ValueError("Source register not A, B, C, D")
                
                # get address for data
                addr = self._regmap[dest].get_val()
                # and change memory to data from src register
                self._memory[addr] = self._regmap[src].get_val()
            
            case 4: # CMP
                # perform comparison and save value
                val = self._regmap[reg].cmp(self._regmap[r1])
                # set corresponding flags
                self._set_flags(val)

            case 5: # CMPI
                imm = self._immediate(inst.args[1], 1)

                # same as regular CMP
                val = self._regmap[reg].cmp(imm)
                self._set_flags(val)

            # JMP, JNZ, JEZ, JNE, JPZ
            case 6 | 7 | 8 | 9 | 10:
                label = inst.args[0]
                if label not in self._labels:
                    raise ValueError("Label not found")
                
                jump = False
                if inst.opidx == 6:
                    jump = True
                elif inst.opidx == 7 and not self._zerof:
                    jump = True
                elif inst.opidx == 8 and self._zerof:
                    jump = True
                elif inst.opidx == 9 and self._negativef:
                    jump = True
                elif inst.opidx == 10 and not self._negativef:
                    jump = True

                if jump:
                    self._index = self._labels[label]
                    inc_pc = False
                
            case 11: # INC
                if reg not in CPU.regs2b:
                    raise ValueError("Register to increment is not X or Y")
                self._regmap[reg].increment()

            case 12: # DEC
                if reg not in CPU.regs2b:
                    raise ValueError("Register to decrement is not X or Y")
                self._regmap[reg].decrement()

            case 13: # INV
                if reg not in CPU.regs1b:
                    raise ValueError("Register to invert is not A, B, C, or D")
                self._regmap[reg].inv()

            case 14: # ADD
                self._reg_check3(dest, r1, r2)
                
                val = self._regmap[dest].add(self._regmap[r1], self._regmap[r2])

                # set flags
                self._set_flags(val)

            case 15: # ADDI
                imm = self._immediate(inst.args[2], 1)

                self._reg_check2(dest, r1)
                
                val = self._regmap[dest].add(self._regmap[r1], imm)

                self._set_flags(val)

            case 16: # SUB
                self._reg_check3(dest, r1, r2)
                
                val = self._regmap[dest].sub(self._regmap[r1], self._regmap[r2])

                self._set_flags(val)

            case 17: # SUBI
                imm = self._immediate(inst.args[2], 1)
                self._reg_check2(dest, r1)
                
                val = self._regmap[dest].sub(self._regmap[r1], imm)

                self._set_flags(val)

            case 18: # ORL
                self._reg_check3(dest, r1, r2)
                
                val = self._regmap[dest].orl(self._regmap[r1], self._regmap[r2])
                # no negative flag set, so do this manually
                if val == 0:
                    self._zerof = True
                else:
                    self._zerof = False
                
            case 19: # ANDL
                self._reg_check3(dest, r1, r2)
                
                val = self._regmap[dest].andl(self._regmap[r1], self._regmap[r2])

                if val == 0:
                    self._zerof = True
                else:
                    self._zerof = False

            case 20: # XORL
                self._reg_check3(dest, r1, r2)
                
                val = self._regmap[dest].xorl(self._regmap[r1], self._regmap[r2])

                if val == 0:
                    self._zerof = True
                else:
                    self._zerof = False

            case _:
                raise ValueError("Unknown instruction index")
        
        if inc_pc:
            self._index += 1

# takes in file name, returns program and memory
def assemble(file_name):
    index = 0
    labels = {}
    memory = [0] * 1024
    program = []
    for line in open(file_name):

        # get rid of newline before anything
        line = line.strip() 

        # ignore comments
        if line.find("--") != -1:
            pos = line.index("--")
            line = line[:pos]

        # ignore if blank
        if line.strip() == "":
            continue

        # check if directive
        if line.find(".") != -1:
            tokens = line.split(" ")
            if tokens[0].lower() == ".byte":
                # ensure proper number of arguments
                if len(tokens) != 3:
                    raise ValueError("Incorrect number of arguments for .byte")
                # get address and data
                addr = int(tokens[1], 0)
                data = int(tokens[2], 0)
                # verify addr and data
                if not 0 <= addr <= 1023:
                    raise ValueError("Address must be within 0 to 1023 (0x000 to 0x3FF)")
                if not -128 <= data <= 255:
                    raise ValueError("Data must be in range -128 to 127 or 0 to 255")
                # place in memory
                memory[addr] = data
            if tokens[0].lower() == ".list":
                # length of list
                length = int(tokens[1], 10)
                if not 0 < length < 11:
                    raise ValueError("Length of list must be positive and not exceed 10")
                # get starting address
                addr = int(tokens[2], 0)
                if (3 + length) != len(tokens):
                    raise ValueError("Incorrect number of arguments for .list")
                for i in range(0, length):
                    data = int(tokens[3 + i], 0)
                    if not -128 <= data <= 255:
                        raise ValueError("Data must be in range -128 to 127 or 0 to 255")
                    memory[addr + i] = int(tokens[3 + i], 0)
                
        # check if label:
        elif line.find(":") != -1:
            # get label name
            name = line.strip().replace(":", "")
            # check if already in dictionary
            if name in labels:
                raise ValueError("Labels must be unique")
            labels[name] = index

        # otherwise, add instruction and increment index
        else:
            program.append(Instruction(line))
            index += 1
    print(labels)
    return (program, memory, labels)
