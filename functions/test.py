from models import FiniteAutomaton, Regex, Int
import functions.registry as registry


@registry.register(registry.FunctionType.EXTRA)
def test(v, regex: Regex, i: Int) -> None:
    raise NotImplementedError('TestFunction not implemented')
