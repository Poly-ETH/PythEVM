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
    
    def peek(self, i: int) -> int:
        """
        Returns a stack element without popping it.
        peek(0) = top element of stack , peek(1) = one after that, and so on...
        """
        if len(self.stack) < i:
            raise StackUnderFlow()
    
        return self.stack[-(i+1)]
    
    def swap(self, i: int) -> None:
        """
        Swaps the top of the stack with the i+1'th element
        """
        if i == 0:
            return

        if len(self.stack) < i:
            raise StackUnderFlow()

        self.stack[-1], self.stack[-(i+1)] = self.stack[-(i+1)], self.stack[-1]

    def __str__(self) -> str:
        return str(self.stack)

    def __repr__(self) -> str:
        return str(self)