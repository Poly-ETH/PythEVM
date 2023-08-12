#!/usr/bin/env python3

"""
Based on web3.py, this script can find addresses of contracts deployed by the `CREATE2` opcode that satisfy a particular predicate.

Usage: `python3 create2.py deployer_addr <salt | predicate> bytecode`

When passing a salt value, this script prints the address of the newly deployed contract based on the deployer address and bytecode hash.

Example: `python3 create2.py Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 42 602a60205260206020f3`

When passing a predicate, this script will search for a salt value such that the new address satisfies the predicate.

Example: `python3 create2.py Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 'lambda addr: "badc0de" in addr.lower()' 602a60205260206020f3`

Another predicate that may be useful: `'lambda addr: addr.startswith("0" * 8)'`

Use with a deployer contract like this:

```solidity
contract Deployer {
    function deploy(bytes memory code, uint256 salt) public returns(address) {
        address addr;
        assembly {
          addr := create2(0, add(code, 0x20), mload(code), salt)
          if iszero(extcodesize(addr)) {
            revert(0, 0)
          }
        }

        return addr;
    }
}
```
"""

from multiprocessing import Pool, Event
from web3 import Web3

import os
import sys


def hexlify(x: int) -> str:
    return "0x" + hex(x)[2:].zfill(64)


def init_pool_processes(the_shutdown_event):
    """
    Initialize each process with the global shutdown event
    """
    global shutdown_event
    shutdown_event = the_shutdown_event


def _create2(deployer, salt_hexstr, hashed_bytecode):
    addr_hexbytes = Web3.keccak(
        hexstr=("ff" + deployer + salt_hexstr + hashed_bytecode)
    )
    addr = Web3.toChecksumAddress(Web3.toHex(addr_hexbytes)[-40:])
    return addr


def init_code_hash(bytecode: str):
    if bytecode.startswith("0x") and len(bytecode) == 66:
        print("🔍 Looks like you passed an initCodeHash, using it directly")
        return bytecode

    return Web3.toHex(Web3.keccak(hexstr=bytecode))


# expecting deployer='aabbccdd' (20 bytes -> 40 characters)
# salt = some decimal number
# bytecode = 'aabbccddeeff...' (variable length)
def create2(deployer, salt, bytecode):
    assert len(deployer) == 40
    assert len(bytecode) % 2 == 0
    salt_hexstr = hex(salt)[2:].zfill(64)
    return _create2(deployer, salt_hexstr, init_code_hash(bytecode)[2:])


class Create2Searcher:
    def __init__(self, deployer_addr, predicate_str, bytecode):
        self.deployer_addr = deployer_addr
        self.predicate_str = predicate_str
        self.hashed_bytecode = init_code_hash(bytecode)[2:]

    def search(self, starting_salt=0):
        predicate = eval(self.predicate_str)
        salt = starting_salt
        print("Starting search with salt:", hexlify(salt))
        while True:
            addr = _create2(self.deployer_addr, hexlify(salt)[2:], self.hashed_bytecode)

            if predicate(addr.lower()):
                print(
                    f"\nFound a match! Deploying with salt={hexlify(salt)} to get address {addr}"
                )
                shutdown_event.set()

            if (salt % 10000) == 0 and shutdown_event.is_set():
                print(f"Stopped searching after {salt - starting_salt} attempts")
                break

            salt += 1


def main():
    if len(sys.argv) != 4:
        print(
            f"""Usage: python3 {sys.argv[0]} deployer_addr <salt | predicate> <bytecode|initCodeHash>

When passing a salt value, this script prints the address of the newly deployed contract based on the deployer address and bytecode hash.
Example: python3 {sys.argv[0]} Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 42 602a60205260206020f3

When passing a predicate, this script will search for a salt value such that the new address satisfies the predicate.
Example: python3 {sys.argv[0]} Bf6cE3350513EfDcC0d5bd5413F1dE53D0E4f9aE 'lambda addr: \"badc0de\" in addr.lower()' 602a60205260206020f3

Another predicate that may be useful: 'lambda addr: addr.startswith(\"0\" * 8)'
"""
        )
        sys.exit(0)

    deployer_addr = sys.argv[1]
    if deployer_addr.startswith("0x"):
        deployer_addr = deployer_addr[2:]

    bytecode = sys.argv[3]

    try:
        salt_str = sys.argv[2]
        salt = int(salt_str, 16) if salt_str.startswith("0x") else int(salt_str)
        print(create2(deployer_addr, salt, bytecode))
        sys.exit(0)
    except ValueError as e:
        pass

    predicate_str = sys.argv[2]
    process_count = os.cpu_count()

    print(f"👷‍♂️ Starting {process_count} worker processes")
    shutdown_event = Event()
    searcher = Create2Searcher(deployer_addr, predicate_str, bytecode)

    with Pool(
        processes=process_count,
        initializer=init_pool_processes,
        initargs=(shutdown_event,),
    ) as pool:
        pool.map(searcher.search, [2**64 * x for x in range(os.cpu_count())])
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
