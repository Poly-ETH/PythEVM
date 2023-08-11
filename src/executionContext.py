from .stack import Stack, InvalidCodeOffset, UnknownOpcode
from .memory import Memory

class ExecutionContext:
    def __init__(self, code=bytes(), pc=0, stack=Stack(), memory=Memory()) -> None:
        self.code = code
        self.pc = pc
        self.stack = stack
        self.memory = memory
        self.stopped = False

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


# Abstract class
class Instruction:
    def __init__(self, opcode: int, name: str) -> None:
        self.opcode = opcode
        self.name = name

    def execute(self, context: ExecutionContext) -> None:
        raise NotImplementedError()
    
INSTRUCTIONS = []
INSTRUCTION_BY_OPCODE = {}

def register_instructions(opcode: int, name: str, execute_func: callable) -> None:
    instruction = Instruction(opcode, name)
    instruction.execute = execute_func
    INSTRUCTIONS.append(instruction)

    assert opcode not in INSTRUCTION_BY_OPCODE
    INSTRUCTION_BY_OPCODE[opcode] = instruction

    return instruction


STOP = register_instructions(0x00, "STOP", lambda ctx: ctx.stop())
PUSH1 = register_instructions(
    0x60,
    "PUSH1",
    lambda ctx: ctx.stack.push(ctx.read_code(1)),
)

ADD = register_instructions(
    0x01,
    "ADD",
    lambda ctx: ctx.stack.push(ctx.stack.pop() + ctx.stack.pop() % 2**256),
)

MUL = register_instructions(
    0x02,
    "MUL",
    lambda ctx: ctx.stack.push((ctx.stack.pop() * ctx.stack.pop()) % 2**256)
)


def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0 or context.pc >= len(context.code):
        raise InvalidCodeOffset({"code": context.code, "pc": context.pc})
    
    opcode = context.read_code(1)
    instruction = INSTRUCTION_BY_OPCODE.get(opcode)
    
    if instruction is None:
        raise UnknownOpcode({"opcode": opcode})
    
    return instruction