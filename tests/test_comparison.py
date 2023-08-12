from smol_evm.constants import MAX_UINT256
from smol_evm.context import ExecutionContext
from smol_evm.opcodes import LT, GT, SLT, SGT, EQ, ISZERO, uint_to_int, int_to_uint

import pytest

from shared import with_stack

@pytest.fixture
def context() -> ExecutionContext:
    return ExecutionContext()

def test_lt_equal(context):
    LT(with_stack(context, [1, 1]))
    assert context.stack.pop() == 0

def test_lt_simple(context):
    LT(with_stack(context, [1, 0]))
    assert context.stack.pop() == 1

def test_gt_equal(context):
    GT(with_stack(context, [1, 1]))
    assert context.stack.pop() == 0

def test_gt_simple(context):
    GT(with_stack(context, [0, 1]))
    assert context.stack.pop() == 1

def test_slt_equal(context):
    SLT(with_stack(context, [int_to_uint(-1), int_to_uint(-1)]))
    assert context.stack.pop() == 0

def test_slt_simple(context):
    SLT(with_stack(context, [10, int_to_uint(-1)]))
    assert context.stack.pop() == 1

def test_slt_extreme(context):
    # MAX_UINT256 is -1
    SLT(with_stack(context, [10, MAX_UINT256]))
    assert context.stack.pop() == 1

def test_sgt_equal(context):
    SGT(with_stack(context, [1, 1]))
    assert context.stack.pop() == 0

def test_sgt_simple(context):
    SGT(with_stack(context, [int_to_uint(-5), 10]))
    assert context.stack.pop() == 1

def test_sgt_extreme(context):
    # MAX_UINT256 is -1
    SGT(with_stack(context, [MAX_UINT256, 10]))
    assert context.stack.pop() == 1

def test_eq_simple(context):
    EQ(with_stack(context, [1, 1]))
    assert context.stack.pop() == 1

def test_eq_big(context):
    EQ(with_stack(context, [MAX_UINT256, MAX_UINT256]))
    assert context.stack.pop() == 1

def test_eq_zero(context):
    EQ(with_stack(context, [0, 0]))
    assert context.stack.pop() == 1

def test_eq_not_equal(context):
    EQ(with_stack(context, [1, 0]))
    assert context.stack.pop() == 0

def test_iszero_zero(context):
    ISZERO(with_stack(context, [1, 0]))
    assert context.stack.pop() == 1

def test_iszero_notzero(context):
    ISZERO(with_stack(context, [0, 1]))
    assert context.stack.pop() == 0
