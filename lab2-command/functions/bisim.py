from functions import registry
from models import FiniteAutomaton
from models.grammar import Grammar


@registry.register(registry.FunctionType.PREDICATE)
def bisim(self: FiniteAutomaton, other: FiniteAutomaton) -> bool:
    g1, g2 = Grammar.from_automaton(self, 'S'), Grammar.from_automaton(other, 'Q')
    return g1.is_bisimilar(g2)[0]
