from codes import *

lines = ["LDI A, 60", "MOV B, A"]
prog = []
for i in lines:
    prog.append(Instruction(i))

memory = [0] * 1024

cpu = CPU(prog, memory, None)

while True:
    print(cpu)
    cpu.step()

