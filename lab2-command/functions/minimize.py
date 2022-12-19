from models import FiniteAutomaton
from functions import registry


@registry.register(registry.FunctionType.REGULAR)
def minimize(self: FiniteAutomaton) -> FiniteAutomaton:
    raise NotImplementedError
