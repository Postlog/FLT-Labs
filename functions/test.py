import dataclasses

from models import FunctionStep, Function


@dataclasses.dataclass
class TestFunctionStep(FunctionStep):
    def __str__(self):
        pass


class TestFunction(Function):
    """
    Функция для примера
    """

    def _call_function(self):
        pass
