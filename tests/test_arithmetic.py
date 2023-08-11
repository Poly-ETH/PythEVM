from src import MAX_UINT256
from src import ExecutionContext
from src import ADD

import pytest

from src.stack import Stack

@pytest.fixture
def context() -> ExecutionContext:
    code = bytes(ADD.opcode)
    return ExecutionContext(code=code)

def test_simple(context):
    ADD.execute(with_stack_contents(context, [1, 2]))
    assert context.stack.pop() == 3

def test_overflow(context):
    ADD.execute(with_stack_contents(context, [1, MAX_UINT256]))
    assert context.stack.pop() == 0

def test_overflow(context):
    ADD.execute(with_stack_contents(context, [3, MAX_UINT256 - 1]))
    assert context.stack.pop() == 1

def with_stack_contents(context, some_iterable):
    for x in some_iterable:
        context.stack.push(x)
    return context