InvalidStackItem = type("InvalidStackItem", (Exception,), {})
StackOverFlow = type("StackOverFlow", (Exception,), {})
StackUnderFlow = type("StackUnderFlow", (Exception,), {})
InvalidMemoryAccess = type("InvalidMemoryAccess", (Exception,), {})
InvalidMemoryValue = type("InvalidMemoryValue", (Exception,), {})
InvalidCodeOffset = type("InvalidCodeOffset", (Exception,), {})
UnknownOpcode = type("UnknownOpcode", (Exception,), {})

MAX_UINT256 = 2**256-1
MAX_UINT8 = 2**8-1