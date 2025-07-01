from codes import CPU, Instruction

prog = []
with open("test.lab7") as f:
    for line in f:
        prog.append(Instruction(line))

memory = [0] * 1024

cpu = CPU(prog, memory, None)

while True:
    print(cpu)
    cpu.step()
    input()

