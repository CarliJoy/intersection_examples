Below I've tried to follow through the logic for what happens if we assume each of the options. I'm trying not to make a statement here about which I prefer just provide clarity, although it is worth noting that option 1 leads to a misleading type.

# Example set up

```py
from typing import TypeVar, Generic
import numpy as np
from dataclasses import dataclass
T = TypeVar("T")

class A:
    @staticmethod
    def bar() -> int:
        return 1

@dataclass
class Test(Generic[T]):
    @staticmethod
    def foo(x: T) -> T & A:
        x.bar = A.bar
        return x
y = np.cos(1) # External library, type is Any here
# Let's assume y has attribute ndim (as it happens it actually does)
```

# 1. T & Any = T
### incorrect

```py
z = Test.foo(x = y) # z has type A
z.ndim # Error does not have attribute ndim, incorrect
```

# 2. T & Any = Any
### correct, but perhaps loses some info

```py
z = Test.foo(x = y) # z has type A
z.ndim # fine - type unknown but this is expected
z.bar() # also fine, although type of return is unknown in bar
```

# 3. T & Any is an error
### correct, maybe a little restrictive
```py
z = Test.foo(x = y) # We get an error here.
```
We can fix this by giving y a type, but it might make code a bit longer sometimes. Is it worth making it longer? Perhaps

# 4. Any is not reduced within intersections.
## Leaves more work for the type checker, but also more flexibility
```py
z = Test.foo(x = y) # z has type Any & A
z.ndim # Fine I think, returns type Any
z.bar() # Returns type of int? If the type checker is smart enough
```

# 5. Any is only considered in an intersection in deference to non-gradual types.

Not sure I'm clear on the difference between this and option 4, perhaps if you could fill out this example @mikeshardmind? Happy to edit this to include.
