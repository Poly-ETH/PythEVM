InvalidStackItem = type("InvalidStackItem", (Exception,), {})
StackOverFlow = type("StackOverFlow", (Exception,), {})
StackUnderFlow = type("StackUnderFlow", (Exception,), {})
InvalidMemoryAccess = type("InvalidMemoryAccess", (Exception,), {})
InvalidMemoryValue = type("InvalidMemoryValue", (Exception,), {})

MAX_UINT256 = 2**256-1
MAX_UINT8 = 2**8-1

class Stack:
    def __init__(self, max_depth=1024) -> None:
        self.stack = []
        self.max_depth = max_depth

    def push(self, item: int) -> None:
        if item < 0 or MAX_UINT256:
            raise InvalidStackItem({"item": item})
        
        if (len(self.stack) + 1 > self.max_depth):
            raise StackOverFlow()
        
        self.stack.append(item)

    def pop(self) -> int:
        if len(self.stack) == 0:
            raise StackUnderFlow()
        
        return self.stack.pop()
    
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