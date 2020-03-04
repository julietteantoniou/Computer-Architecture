"""CPU functionality."""

import sys

"""OP CODES"""
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
ADD = 0b10100000
SUB = 0b10100001
HLT = 0b00000001
PSH = 0b01000101
POP = 0b01000110
CLL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101
PRA = 0b01001000
AND = 0b10101000
XOR = 0b10101011

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.halt = False
        self.sp = 7
        self.FL = 0b00000000 #`FL` bits: `00000LGE`

        # self.SP = self.reg[7]

        self.branchtable = {
            LDI: self.LDI,
            PRN: self.PRN,
            MUL: self.MUL,
            ADD: self.ADD,
            SUB: self.SUB,
            HLT: self.HLT,
            PSH: self.PSH,
            POP: self.POP,
            CLL: self.CLL,
            RET: self.RET,
            CMP: self.CMP,
            JMP: self.JMP,
            JNE: self.JNE,
            JEQ: self.JEQ,
            PRA: self.PRA,
            AND: self.AND,
            XOR: self.XOR
        }
        

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        program = []

        if len(sys.argv) != 2:
            print('Error')
            sys.exit()

        with open(sys.argv[1]) as program:
            for instruction in program:
                seperate_comment = instruction.split('#') #separate out comments if any
                instruction = seperate_comment[0].strip() #remove white space from what's left
                if instruction == '': #if it's a comment or a blank line, ignore and keep going
                    continue
                int_value = int(instruction, 2) #convert binary string to integer

                self.ram[address] = int_value
                address += 1

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def MUL(self):
        self.alu('MUL')
        self.pc += 3

    def ADD(self):
        self.alu('ADD')
        self.pc +=3

    def SUB(self):
        self.alu('SUB')
        self.pc += 3

    def AND(self):
        self.alu('AND')
        self.pc += 3

    def XOR(self):
        self.alu('XOR')
        self.pc += 3

    def LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def HLT(self):
        self.halt = True

    def alu(self, op):
        """ALU operations."""
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        
        elif op == 'DIV':
            if self.reg[reg_b] == 0:
                print('error- dividing by 0')
                self.halt = True
            else:
                self.reg[reg_a] /= self.reg[reg_b]
        
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.FL = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL = 0b00000010
            else:
                print('error')

        elif op == 'AND':
            self.reg[reg_a] &= self.reg[reg_b]

        elif op == 'XOR':
            self.reg[reg_a] ^= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def PSH(self):
        self.reg[self.sp] -= 1
        reg_num = self.ram[self.pc + 1]
        reg_val = self.reg[reg_num]
        self.ram[self.reg[self.sp]] = reg_val

        self.pc += 2

    def POP(self):
        val = self.ram[self.reg[self.sp]]
        reg_num = self.ram[self.pc + 1]
        self.reg[reg_num] = val
        self.reg[self.sp] += 1
  
        self.pc += 3

    def CLL(self):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

        self.pc += 3

    def RET(self):
        self.pc= self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

        self.pc += 3

    def CMP(self):
        self.alu('CMP')

        self.pc += 3

    def JMP(self):
        register = self.ram_read(self.pc + 1)
        self.pc = self.reg[register]

    def JNE(self):
        if self.FL != 0b00000001:
            self.JMP()
        else:
            self.pc += 2

    def JEQ(self):
        if self.FL == 0b00000001:
            self.JMP()
        else:
            self.pc += 2

    def PRA(self):
        reg = self.ram_read(self.pc + 1)
        print_char = self.reg[reg]
        print(chr(print_char))       
        self.pc += 2

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.halt == False:
            IR = self.ram[self.pc]
            # operand_a = self.ram_read(self.pc + 1)
            # operand_b = self.ram_read(self.pc + 2)

            # if IR ==  0b10000010: #LDI
            #     self.reg[operand_a] = operand_b
            #     self.pc += 3

            # elif IR == 0b01000111: # PRN
            #     print(self.reg[operand_a])
            #     self.pc += 2

            # elif IR == 0b10100010: #MUL
            #     mul = self.reg[operand_a] * self.reg[operand_b]
            #     self.reg[operand_a] = mul
            #     self.pc += 3

            # if IR == 0b00000001: #HLT
            #     self.halt= True

            if IR in self.branchtable:
                self.branchtable[IR]()

            else:
                print(f'Unknown instruction {self.pc} {self.ram[self.pc]}')
                # self.trace()
                sys.exit()
