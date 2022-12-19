from functions.determinize import determinize
from functions.equal import equal
from functions.minimize import minimize
from functions.thompson import Thompson
from models import FiniteAutomaton, Regex
from functions import registry


@registry.register(registry.FunctionType.PREDICATE)
def equiv(self: FiniteAutomaton | Regex, other: FiniteAutomaton | Regex) -> bool:
    if isinstance(self, FiniteAutomaton) and isinstance(other, FiniteAutomaton):
        return __equiv_nfa(self, other)
    elif isinstance(self, Regex) and isinstance(other, Regex):
        self_nfa, other_nfa = Thompson(self), Thompson(other)
        return __equiv_nfa(self_nfa, other_nfa)
    else:
        raise TypeError(
            f'Ожидались аргументы типов (Regex, Regex) или (FiniteAutomaton, FiniteAutomaton), '
            f'получили: {type(self)} и {type(other)}'
        )


def __equiv_nfa(self: FiniteAutomaton, other: FiniteAutomaton) -> bool:
    self_min_dfa = minimize(determinize(self))
    other_min_dfa = minimize(determinize(other))
    return equal(self_min_dfa, other_min_dfa)
