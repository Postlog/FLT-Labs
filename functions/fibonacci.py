import dataclasses
from datetime import datetime
import typing

from models import Function, Int, FunctionStep, NFA, Regex, NullableBool


@dataclasses.dataclass
class FibonacciFunctionStep(FunctionStep):
    """
    Шаг функции для примера
    """

    n: int
    timestamp: float

    def __str__(self) -> str:
        return f'n={self.n} at: {datetime.fromtimestamp(self.timestamp)}'


class FibonacciFunction(Function):
    """
    Функция для примера: подсчет n-ого числа Фибоначчи
    """

    def _call_function(self, n: Int) -> Int:
        self.steps.append(FibonacciFunctionStep(n.value, datetime.now().timestamp()))

        if n.value <= 0:
            return Int(-1)
        elif n.value == 1:
            return Int(0)
        elif n.value == 2:
            return Int(1)
        else:
            v1, v2 = self._call_function(Int(n.value - 1)), self._call_function(Int(n.value - 2))
            return Int(v1.value + v2.value)
