"""CPU functionality."""

import sys

# setup constants for op codes
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
ADD = 0b10100000
POP = 0b01000110
RET = 0b00010001
PUSH = 0b01000101
CALL = 0b01010000

SP = 7  # stack pointer set to be used a R7 per spec


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # create 8 registers
        self.reg = [0] * 8
        # create 256 bytes of memory
        self.ram = [0] * 256
        # create a program counter (pc)
        self.pc = 0

    def ram_read(self, addr):
        return self.ram[addr]

    def write_ram(self, addr, value):
        self.ram[addr] = value

    def load(self, file_name):
        """Load a program into memory."""
        try:
            address = 0
            # open the file
            with open(file_name) as f:
                for line in f:
                    # srtip out white space, and split at a inline comment
                    cleaned_line = line.strip().split("#")
                    # grab the string number
                    value = cleaned_line[0].strip()

                    # check if value is blank or not, if it is skip onto the next line
                    if value != "":
                        # cast the number string to type int
                        num = int(value, 2)  # we need to convert a binary string to a number ex. "100000010"
                        self.ram[address] = num
                        address += 1
                    else:
                        continue

        except FileNotFoundError:
            print("ERR: FILE NOT FOUND")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self, file_name):
        """Run the CPU."""

        # load the program into memory
        self.load(file_name)
        # var to type less out in the while loop
        read_ram = self.ram_read
        write_ram = self.write_ram

        # run the program
        while True:

            # simple var to type less
            pc = self.pc
            # que an operation to start at default is 0
            op = read_ram(pc)

            if op == LDI:
                self.reg[read_ram(pc + 1)] = read_ram(pc + 2)
                self.pc += 3
            elif op == PRN:
                print(self.reg[read_ram(pc + 1)])
                self.pc += 2
            elif op == MUL:
                # access 2 ergisters and multiply them
                # grab the ram values, that hold the register index's we need
                reg_a = read_ram(pc + 1)
                reg_b = read_ram(pc + 2)
                # call on the ALU
                self.alu("MUL", reg_a, reg_b)
                # move program counter
                self.pc += 3
            elif op == ADD:
                # access 2 registers and add them
                reg_a = read_ram(pc + 1)
                reg_b = read_ram(pc + 2)
                # call the ALU
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3
            elif op == PUSH:
                # decrement SP
                self.reg[SP] -= 1
                # get current mem address SP points to
                stack_addr = self.reg[SP]
                # grab a reg number from the instruction
                reg_num = read_ram(pc + 1)
                # get the value out of the register
                val = self.reg[reg_num]
                # write the reg value to a postition in the stack
                write_ram(stack_addr, val)
                self.pc += 2
            elif op == POP:
                # get the value out of memory
                stack_val = read_ram(self.reg[SP])
                # get the register number from the instruction in memory
                reg_num = read_ram(pc + 1)
                # set the value of a register to the value held in the stack
                self.reg[reg_num] = stack_val
                # increment the SP
                self.reg[SP] += 1
                self.pc += 2
            elif op == CALL:
                # decrement the SP
                self.reg[SP] -= 1
                # get the current mem addr that SP points to
                stack_addr = self.reg[SP]
                # get the return mem addr
                return_addr = pc + 2
                # push the return addr onto the stack
                write_ram(stack_addr, return_addr)
                # set PC to the value in the register
                reg_num = read_ram(pc + 1)
                self.pc = self.reg[reg_num]
            elif op == RET:
                # pop the return mem addr off the stack
                # store the poped mem addr in the PC
                self.pc = read_ram(self.reg[SP])
                self.reg[SP] += 1
            elif op == HLT:
                sys.exit(1)
            else:
                print("ERR: UNKNOWN COMMAND:\t", op)


if len(sys.argv) == 2:

    file_name = sys.argv[1]

    c = CPU()
    # set the mem address the stack pointer is looking at.
    c.reg[SP] = 0xf4
    c.run(file_name)
else:
    # err message
    print("""
ERR: PLEASE PROVIDE A FILE THAT YOU WISH TO RUN\n
ex python cpu.py examples/FILE_NAME
""")
    sys.exit(2)

# file_name = "examples/call.ls8"

# c = CPU()
# # set the mem address the stack pointer is looking at.
# c.reg[SP] = 0xf4
# c.run(file_name)
