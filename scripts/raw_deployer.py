#!/usr/bin/env python3

"""
Takes the binary representation of a contract and generates the init code that will deploy that contract (Ti in Yellow Paper terminology).

For instance, let's say that you have some Yul code, that when compiled with `solc` has the following binary representation: `602a60205260206020f3`.

```
> python raw_deployer.py 602a60205260206020f3
600a8061000d6000396000f3fe602a60205260206020f3
```

You can now deploy this code:

```javascript
web3.eth.sendTransaction({
    from: /* your address */,
    /* no to address as we are creating a contract */
    data: "600a8061000d6000396000f3fe602a60205260206020f3"
})
```

Wait for the transaction to be confirmed, and go look at the code of the contract that was deployed, it should match our compiled Yul code `602a60205260206020f3` 🙌
"""

import string
import sys


def bin2(value):
    return binN(value, 2)


def bin4(value):
    return binN(value, 4)


def binN(value, N):
    assert N % 2 == 0
    return "{:x}".format(value).zfill(N)


class Instruction:
    def __init__(self, opcode, arg_length=None, arg=None):
        self.opcode = opcode
        self.arg_length = arg_length
        self.arg = arg

    def to_bin(self):
        if self.arg is None:
            return bin2(self.opcode)

        return bin2(self.opcode) + binN(self.arg, 2 * self.arg_length)


class Block:
    def __init__(self, instructions):
        self.instructions = instructions

    def to_bin(self):
        return "".join([x.to_bin() for x in self.instructions])


def PUSH1(arg):
    return Instruction(0x60, 1, arg)


def PUSH2(arg):
    return Instruction(0x61, 2, arg)


DUP1 = Instruction(0x80)
CODECOPY = Instruction(0x39)
RETURN = Instruction(0xF3)
INVALID = Instruction(0xFE)


def main():
    runtime_bin = sys.argv[1]
    assert len(runtime_bin) % 2 == 0
    assert all([x in string.hexdigits for x in runtime_bin])

    # in bytes
    runtime_bin_length = len(runtime_bin) // 2

    # PUSH2 ought to be enough for anybody
    push_length = (
        PUSH1(runtime_bin_length)
        if runtime_bin_length <= 0xFF
        else PUSH2(runtime_bin_length)
    )

    # we need to see how long the init code is first and then we can backfill this
    push_offset = PUSH1(0)

    initcode = Block(
        [
            push_length,
            DUP1,
            push_offset,
            PUSH1(0),  # mem destination
            CODECOPY,  # copies code[runtime_bin_offset .. offset + runtime_bin_length] to mem[0]
            PUSH1(0),
            RETURN,  # returns mem[0 .. runtime_bin_length]
            INVALID,  # not stricly necessary, but makes it easier to find the end
        ]
    )

    # since runtime_bin will come right after the init code, runtime_bin_offset is just the init code length
    initcode_length = len(initcode.to_bin()) // 2
    push_offset.arg = initcode_length

    print(initcode.to_bin() + runtime_bin)


if __name__ == "__main__":
    main()
