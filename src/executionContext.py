from .stack import Stack, InvalidCodeOffset, UnknownOpcode, InvalidMemoryAccess
from .memory import Memory
from .opcodesInstructions import *

class ExecutionContext:
    def __init__(self, code=bytes(), pc=0, stack=Stack(), memory=Memory()) -> None:
        self.code = code
        self.pc = pc
        self.stack = stack
        self.memory = memory
        self.stopped = False
        self.return_data = bytes

    def stop(self) -> None:
        self.stopped = True
    
    def read_code(self, num_bytes) -> int:
        """
        Returns the next num_bytes from the code buffer as an integer and advanced pc by num_bytes
        """
        # Read num_bytes from code buffer starting at pc and upto pc + num_bytes, 
        # byteorder="big" means big endian (most significant byte first)
        value = int.from_bytes(self.code[self.pc: self.pc + num_bytes], byteorder="big")
        self.pc += num_bytes
        
        return value
    
    def set_return_data(self, offset: int, length: int) -> None:
        self.stopped = True
        self.return_data = self.memory.load_range(offset, length)

    def __str__(self) -> str:
        return "stack: " + str(self.stack) + "\n" + "memory: " + str(self.memory) + "\n" + "pc: " + str(self.pc) + "\n" + "code: " + str(self.code) + "\n" + "stopped: " + str(self.stopped) + "\n" + "return_data: " + str(self.return_data)

    def __repr__(self) -> str:
        return str(self)


def valid_jump_destinations(code: bytes) -> set[int]:
    jumpdests = set()
    for i in range(len(code)):
        current_opcode = code[i]
        if current_opcode == JUMPDEST.opcode:
            i += current_opcode - PUSH1.opcode + 1
        elif PUSH1.opcode <= current_opcode <= PUSH32.opcode:
            i += current_opcode - PUSH1.opcode + 2
        
        i += 1

        return jumpdests
