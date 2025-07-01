# Architecture
- 4 general purpose registers, A B C D, 1 byte each (Referred to as R)
- 2 memory access registers, X Y, 2 bytes each (Referred to as S)
  - These registers can be loaded with values above 1023, but when accessing memory, it will wrap around (ex. 1024 corresponds to address 0)
- 1024 bytes of memory available, requires upper 2 bits of memory access registers
- Flags based on last operation: Negative, Zero
    - If result of an operation is Zero, Zero flag = 1, otherwise 0
    - If the MSB of a result is 1, then Negative flag = 1, otherwise 0
    - Data management instructions such as MOV or LDI do **not** set the flags, only logic/arithmetic operations do

# Instructions

## Data Management
- `MOV R1/S1, R2/S2`
  - Move data from register `R2/S2` to register `R1/S1`, registers must be same width
  - Ex. `MV X, Y` is good, `MV X, A` is not good
- `LDI R/S, IMM`
  - Load register `R/S` with specified immediate in hex (0x), binary (0b), or decimal (no prefix)
  - Can load values -128 to 127 or 0 to 255 into A, B, C, D
  - Can load values 0 to 65535 into X, Y, with memory wraparound
  - 1 byte immediate for A, B, C, D, 2 byte immediate for X, Y
- `RDM R, S`
  - Read memory from address `S` and load into register `R`
- `WRM S, R`
  - Write data in register `R` to address `S`

## Branching
- `JMP LABEL`
  - Jumps to instruction immediately following specified label
- `JNZ LABEL`
  - Jumps to instruction immediately following specified label **if** the Zero flag is 0, otherwise continues execution
- `JEZ LABEL`
  - Jumps to instruction immediately following specified label **if** the Zero flag is 1, otherwise continues execution
- `JNE LABEL`
  - Jumps to instruction immediately following specified label **if** the Negative flag is 1, otherwise continues execution
- `JPZ LABEL`
  - Jumps to instruction immediately following specified label **if** the Negative flag is 0, otherwise continues execution

## Logic/Arithmetic Operations

- `ADD R1, R2, R3`
  - R1 = R2 + R3, sets zero flag and negative flag
- `ADDI R1, R2, IMM`
  - R1 = R2 + IMM, sets zero flag and negative flag
- `SUB R1, R2, R3`
  - R1 = R2 - R3, sets zero flag a nd negative flag
- `SUBI R1, R2, IMM`
  - R1 = R2 - IMM, sets zero flag and negative flag
- `INC S`
  - Increments X or Y register, does not set zero flag or negative flag
- `DEC S`
  - Decrements X or Y register, does not set zero flag or negative flag
- `ORL R1, R2, R3`
  - R1 = R2 OR R3, bitwise or, sets zero flag but not negative flag
- `ANDL R1, R2, R3`
  - R1 = R2 AND R3, bitwise and, sets zero flag but not negative flag
- `XORL R1, R2, R3` 
  - R1 = R2 XOR R3, bitwise xor, sets zero flag but not negative flag
- `INV R1`
  - R1 = ~R1 (bitwise not), does not set zero flag or negative flag
- `CMP R1, R2`
  - If R1 == R2, sets zero flag and not negative flag
  - If R1 > R2, sets neither flag
  - If R1 < R2, sets negative flag
- `CMPI R1, IMM`
  - If R1 == IMM, sets zero flag and not negative flag
  - If R1 > IMM, sets neither flag
  - If R1 < IMM, sets negative flag

# Directives

All directives aside from labels should be at the beginning of the program for proper usage.

## Labels
Must be on a separate line from other code and must contain a colon. Labels must also be unique.

Valid:
```
LDI A, 0x05
LDI B, 0x00
LOOP:
ADD B, B, A
SUBI A, A, 1
JNZ LOOP
```
Invalid:
```
LDI A, 0x05
LDI B, 0x00
LOOP: ADD B, B, A
SUBI A, A, 1
JNZ LOOP
```
Because the `LOOP` directive is on the same line as an instruction, it does not function properly.

## .byte ADDR DATA
Places `DATA` at address `ADDR` within data. `ADDR` and `DATA` can either be in hexadecimal (prefixed by 0x), binary (prefixed by 0b), or decimal (no prefix). `ADDR` must be a non-negative value less than or equal to 1023 (0x3FF), and `DATA` must be less than or equal to 255 (0xFF) for unsigned, or between 128 and -127 for signed. Negative values will be put in the register as 2's complement values.

Valid:
```
.byte 10 0b11
.byte 0x10 11
.byte 0b10 0x11
```

Invalid:
```
.byte 10
.byte 0x10 500
.byte 2000 0x10
```
The first example has only 1 argument, the second has a value of `DATA` over 256, and the third has an `ADDR` greater than 1023 (0x3FF in hex). 

## .list LENGTH ADDR DATA0 DATA1...
Places a list of length `LENGTH` with `DATA0` at address `ADDR`, `DATA1` at address `ADDR + 1`, etc. The max length for a list is a length of 10, then a new list must be created with another directive. The entries for the list **must** be on the same line to function properly. The length of the list must be in decimal, while the data and address can be in hexadecimal, binary, or decimal.

Valid:
```
.list 5 0x100 0x08 0x09 0x0A 0x0B 0x0C
.list 3 0x200 0x10 0x20 0x30
```

Invalid:
```
.list 3
.list 400 0x0B
.list 6 0xFF 0x0A 0x0B 0x0C 0x0D
0x0E 0x0F
```

In the first example, no address and no list elements are given. In the second, the length is over 10 and there are no list elements. In the third example, an address is given and the length is valid, but the list elements go over multiple lines.