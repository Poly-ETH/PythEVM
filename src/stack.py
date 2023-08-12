from .generics import *

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
