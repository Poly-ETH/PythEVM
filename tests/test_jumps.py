from smol_evm.opcodes import *
from smol_evm.runner import run, ExecutionLimitReached

import pytest


def test_simple_jump():
    """just jump to the JUMPDEST"""
    # 6003565b
    code = assemble([
        PUSH(3),
        JUMP,
        JUMPDEST
    ])
    ret = run(code).returndata
    assert ret == b""

def test_jump_hyperspace():
    """jump way out into the void"""
    # 602a56
    code = assemble([
        PUSH(42),
        JUMP
    ])
    ctx = run(code)
    assert ctx.success is False

def test_jump_into_push_arg():
    """can only jump on instructions boundaries, so can't fool the EVM by packing a JUMPDEST in a PUSH argument"""
    # 605b600156
    code = assemble([
        PUSH(0x5B),
        PUSH(1),
        JUMP
    ])
    ctx = run(code)
    assert ctx.success is False

def test_jump_over_data():
    """can't jump over sneaky data"""
    # 600456605b00
    code = assemble([
        PUSH(4),
        JUMP,

        # this PUSH1 is not reachable but it "eats" the JUMPDEST,
        # which makes it not a valid JUMPDEST
        PUSH1_OPCODE,

        JUMPDEST,
        STOP
    ])
    ctx = run(code, verbose=True)
    assert ctx.success is False
    assert ctx.reason is not None and ctx.reason.startswith('Invalid jump')
    assert ctx.pc == 3

def test_invalid_jump_dest_in_branch_not_taken():
    """we know we can check for invalid jump destinations, but what if we don't take the branch?"""
    # 6000602a57
    code = assemble([
        PUSH(0),  # cond
        PUSH(42), # target (bad)
        JUMPI
    ])
    ret = run(code).returndata
    assert ret == b""

def test_infinite_loop():
    # 5b600056
    code = assemble([
        JUMPDEST,
        PUSH(0),
        JUMP
    ])
    with pytest.raises(ExecutionLimitReached) as excinfo:
        run(code, max_steps=100)

def test_simple_jumpi_not_taken():
    # 6000600f57602a60005360016000f35b
    code = assemble([
        PUSH(0),  # cond
        PUSH(15), # target
        JUMPI,

        PUSH(42), # mem value
        PUSH(0),  # mem offset
        MSTORE8,
        PUSH(1),  # mem length
        PUSH(0),  # mem offset
        RETURN,

        JUMPDEST
    ])

    ret = run(code).returndata
    assert int.from_bytes(ret, 'big') == 42

def test_simple_jumpi_taken():
    """we're going straight to the end"""
    # 6001600f57602a60005360016000f35b
    code = assemble([
        PUSH(1),  # cond
        PUSH(15), # target
        JUMPI,

        PUSH(42), # mem value
        PUSH(0),  # mem offset
        MSTORE8,
        PUSH(1),  # mem length
        PUSH(0),  # mem offset
        RETURN,

        JUMPDEST
    ])

    ret = run(code, verbose=True).returndata
    assert ret == b""


def test_four_squared():
    # 60048060005b8160125760005360016000f35b8201906001900390600556
    code = assemble([
                    # stack
        PUSH(4),   # n=4
        DUP1,       # n=4, loops=4
        PUSH(0),   # n=4, loops=4, result=0

        # loop_cond
        # if loops != 0, jump to loop_body
        JUMPDEST,
        DUP2,       # n, loops, result, loops
        PUSH(18),  # n, loops, result, loops, loop_body
        JUMPI,      # n, loops, result

        # store result in memory[0]
        PUSH(0),   # n, loops, result, m_result
        MSTORE8,    # n, loops

        # return memory[0]
        PUSH(1),   # n, loops, mem_length
        PUSH(0),   # n, loops, mem_length, mem_offset
        RETURN,

        # loop_body
        JUMPDEST,

        # result += n
        DUP3,       # n, loops, result, n
        ADD,        # n, loops, result'=n+result

        # loops -= 1
        SWAP1,      # n, result', loops
        PUSH(1),   # n, result', loops, 1
        SWAP1,      # n, result', 1, loops
        SUB,        # n, result', loops'=loops-1

        # restore stack
        SWAP1,      # n, loops', result'

        # jump to loop_cond
        PUSH(5),   # n, loops', result', loop_cond
        JUMP,       # -> back to loop_cond
    ])

    ret = run(code, verbose=True, max_steps=200).returndata
    assert int.from_bytes(ret, 'big') == 4 * 4

