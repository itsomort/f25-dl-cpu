from codes import CPU, assemble
import sys

skip = False
filename = "program.lab7"

if len(sys.argv) != 1:
    if sys.argv[1] == "-h":
        print("-h: print this help menu")
        print("-f [filename]: pass in a filename to assemble (no spaces), otherwise defaults to program.lab7")
        print("-s: skips inputting commands")

    if "-s" in sys.argv:
        skip = True
    
    if "-f" in sys.argv:
        idx = sys.argv.index("-f")
        filename = sys.argv[idx + 1]

args = assemble(filename)
cpu = CPU(*args)

def menu():
    print("Available commands:")
    print("If stuck in an infinite loop, CTRL+C or CMD+. to stop the program completely")
    print("Enter memory address in hexadecimal prefixed by 0x to output that memory value")
    print("Enter Q to stop execution, enter S to step, enter C to continue until end")
    print("Enter P to print the state of the cpu, enter H for a reminder of this menu\n")


if not skip:
    menu()

while True:
    print(cpu)
    cont = False
    if not skip:
        while not cont:
            inp = input("Command: ")
            inp = inp.strip().upper()
            if inp.find("X") != -1:
                try:
                    addr = int(inp, 0)
                    if not 0 <= addr <= 1023:
                        raise ValueError()
                    
                    data = cpu._memory[addr]
                    print(f"{hex(addr)}: {data}")
                except ValueError:
                    print("Invalid memory address")
                    continue
                
            if inp == "Q":
                print("Stopping execution")
                print(cpu)
                exit()
            if inp == "S":
                cont = True
            if inp == "C":
                cont = True
                skip = True
            if inp == "P":
                print(cpu)
            if inp == "H":
                menu()
    try:
        cpu.step()
    except Exception as e:
        if isinstance(e, EOFError):
            exit()
        inst = cpu._program[cpu._index]
        print(f"Error in instruction: {inst}")
        print(e)
        exit()

