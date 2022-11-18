from models import FiniteAutomaton
from functions import registry


@registry.register(registry.FunctionType.REGULAR)
def determinize(self: FiniteAutomaton) -> FiniteAutomaton:
    raise NotImplementedError
