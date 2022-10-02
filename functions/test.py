import dataclasses
import typing

from models import FunctionStep, Function, NFA, Regex, Int


@dataclasses.dataclass
class TestFunctionStep(FunctionStep):
    def __str__(self):
        pass


class TestFunction(Function):
    """
    Функция для примера
    """

    def _call_function(self, v: typing.Union[NFA, Regex], regex: Regex, i: Int) -> None:
        raise NotImplementedError('TestFunction not implemented')
