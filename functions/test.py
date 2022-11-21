from typing import Union

from models import FiniteAutomaton, Regex, Int
import functions.registry as registry


@registry.register(registry.FunctionType.EXTRA)
def test(v: Union[FiniteAutomaton, Regex], regex: Regex, i: Int) -> None:
    raise NotImplementedError('TestFunction not implemented')
