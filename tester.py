from codes import CPU, assemble

args = assemble("test.lab7")
cpu = CPU(*args)

while True:
    print(cpu)
    input()
    cpu.step()

