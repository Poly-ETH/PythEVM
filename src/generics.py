InvalidStackItem = type("InvalidStackItem", (Exception,), {})
StackOverFlow = type("StackOverFlow", (Exception,), {})
StackUnderFlow = type("StackUnderFlow", (Exception,), {})
InvalidMemoryAccess = type("InvalidMemoryAccess", (Exception,), {})
InvalidMemoryValue = type("InvalidMemoryValue", (Exception,), {})
InvalidCodeOffset = type("InvalidCodeOffset", (Exception,), {})
UnknownOpcode = type("UnknownOpcode", (Exception,), {})

from dataclasses import dataclass

from .executionContext import ExecutionContext


@dataclass
class EVMException(Exception):
    context: ExecutionContext


class UnknownOpcode(EVMException):
    ...


class InvalidCodeOffset(EVMException):
    ...


@dataclass
class InvalidJumpDestination(EVMException):
    target_pc: int

MAX_UINT256 = 2**256-1
MAX_UINT8 = 2**8-1
MAX_STACK_DEPTH = 1024

def is_valid_uint256(value: int) -> bool:
    return 0 <= value <= MAX_UINT256

def is_valid_uint8(value: int) -> bool:
    return 0 <= value <= MAX_UINT8