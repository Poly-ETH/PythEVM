from .generics import *
from .executionContext import ExecutionContext

# Abstract class
class Instruction:
    def __init__(self, opcode: int, name: str) -> None:
        self.opcode = opcode
        self.name = name

    def execute(self, context: ExecutionContext) -> None:
        raise NotImplementedError()
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.name
    
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

MSTORE8 = register_instructions(
    0x53,
    "MSTORE8",
    lambda ctx: ctx.memory.store(ctx.stack.pop(), ctx.stack.pop() % 2**8)
)

RETURN = register_instructions(
    0xf3,
    "RETURN",
    lambda ctx: ctx.set_return_data(ctx.stack.pop(), ctx.stack.pop())
)

def decode_opcode(context: ExecutionContext) -> Instruction:
    if context.pc < 0: # or context.pc >= len(context.code):
        raise InvalidCodeOffset({"code": context.code, "pc": context.pc})
    
    # section 9.4.1 of the yellow paper, the operation to be executed if pc is outside code is STOP
    if context.pc >= len(context.code):
        return STOP

    opcode = context.read_code(1)
    instruction = INSTRUCTION_BY_OPCODE.get(opcode)
    
    if instruction is None:
        raise UnknownOpcode({"opcode": opcode})
    
    return instruction