from models import FiniteAutomaton
from functions import registry


@registry.register(registry.FunctionType.PREDICATE)
def equal(self: FiniteAutomaton, other: FiniteAutomaton) -> bool:
    raise NotImplementedError
