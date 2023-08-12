from .stack import MAX_UINT256, MAX_UINT8, InvalidMemoryAccess, InvalidMemoryValue
from .generics import is_valid_uint256, is_valid_uint8

ZERO_WORD = [0] * 32

# thanks, https://stackoverflow.com/questions/14822184/is-there-a-ceiling-equivalent-of-operator-in-python
def ceildiv(a, b):
    return -(a // -b)

class Memory:
    def __init__(self) -> None:
        self.memory = []

    def store(self, offset: int, value: int) -> None:
        if offset < 0 or offset >  MAX_UINT256:
            raise InvalidMemoryAccess({"offset": offset})
    
        if value < 0 or value > MAX_UINT8:
            raise InvalidMemoryValue({"offset": offset, "value": value})
        
        # expand memory is needed
        if offset >= len(self.memory):
            self.memory.extend([0] * (offset - len(self.memory) + 1))
        
        self.memory[offset] = value

    def store_word(self, offset: int, value: int) -> None:
        _validate_offset(offset)
        if not is_valid_uint256(value):
            raise InvalidMemoryValue({"offset": offset, "value": value})

        self._expand_if_needed(offset + 31)
        for i in range(0, 32):
            self.memory[offset + 31 - i] = value & (0xFF << (i * 8))

    def load(self, offset: int) -> int:
        if offset < 0:
            raise InvalidMemoryAccess({"offset": offset})
        if offset >= len(self.memory):
            return 0
        
        return self.memory[offset]
    
    def load_word(self, offset: int) -> int:
        return int.from_bytes(self.load_range(offset, 32), "big")


    def load_range(self, offset: int, length: int) -> bytes:
        if offset < 0:
            raise InvalidMemoryAccess({"offset": offset})

        # we could use a slice here, but this lets us gets 0 bytes if we read past the end of concrete memory
        return bytes(self.load(x) for x in range(offset, offset + length))

    def active_words(self) -> int:
        return len(self.memory) // 32

    # per the definition of MSTORE8 and MLOAD in the yellow paper, the number of active words is
    # expanded when both reading and writing a previously untouched memory location
    # MLOAD:
    #   μ′i ≡ max(μi,⌈(μs[0]+32)÷32⌉)
    # MSTORE8:
    #   μ′i ≡ max(μi, ⌈(μs[0]+1)÷32⌉)
    #
    # human-readable Solidity docs:
    # https://docs.soliditylang.org/en/latest/introduction-to-smart-contracts.html#storage-memory-and-the-stack
    def _expand_if_needed(self, offset: int) -> None:
        if offset < len(self.memory):
            return

        active_words_after = max(self.active_words(), ceildiv(offset + 1, 32))

        self.memory.extend(ZERO_WORD * (active_words_after - self.active_words()))

        assert len(self.memory) % 32 == 0


    def __str__(self) -> str:
        return str(self.memory)

    def __repr__(self) -> str:
        return str(self)
    

def _validate_offset(offset: int) -> None:
    if not is_valid_uint256(offset):
        raise InvalidMemoryAccess({"offset": offset})
