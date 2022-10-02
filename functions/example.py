import dataclasses
from datetime import datetime
import typing

from models import Function, Int, FunctionStep, NFA, Regex, NullableBool


@dataclasses.dataclass
class ExampleFunctionStep(FunctionStep):
    """
    Шаг функции для примера
    """

    index: int
    timestamp: float

    def __str__(self) -> str:
        return f'Index: {self.index} Date: {datetime.fromtimestamp(self.timestamp)}'


class ExampleFunction(Function):
    """
    Функция для примера
    """

    def _call_function(
            self,
            a: typing.Union[NFA, Regex],
            regex: Regex, number: Int,
    ) -> typing.Tuple[NullableBool, Int]:
        for i in range(number.value):
            self.steps.append(ExampleFunctionStep(i, datetime.now().timestamp()))

        return NullableBool(None), number
