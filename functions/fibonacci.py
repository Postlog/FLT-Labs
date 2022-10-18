from models import Int
import functions.registry as registry


@registry.register(registry.FunctionType.REGULAR)
def fibonacci(n: Int) -> Int:
    if n.value < 0:
        raise ValueError()

    if n.value < 2:
        return Int(n.value)

    v1, v2 = fibonacci(Int(n.value - 1)), fibonacci(Int(n.value - 2))
    return Int(v1.value + v2.value)
