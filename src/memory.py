from .stack import MAX_UINT256, MAX_UINT8, InvalidMemoryAccess, InvalidMemoryValue

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

        