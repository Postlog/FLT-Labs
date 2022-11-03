import networkx as nx
from itertools import product

from functions import registry
from models import FiniteAutomaton, Regex


# Потом заменим на реальные функции
class Deps:
    @staticmethod
    def determinize(self: FiniteAutomaton) -> FiniteAutomaton:
        return FiniteAutomaton()

    @staticmethod
    def glushkov(self: Regex) -> FiniteAutomaton:
        return FiniteAutomaton()


@registry.register(registry.FunctionType.PREDICATE)
def subset(self: FiniteAutomaton | Regex, other: FiniteAutomaton | Regex) -> bool:
    """Проверить, является ли первый НКА/регулярка подмножеством второго НКА/регулярки."""
    if not (
        type(self) == type(other)
        and (isinstance(self, Regex) or isinstance(self, FiniteAutomaton))
    ):
        raise ValueError(
            f'Ожидались аргументы типов (Regex, Regex) или (FiniteAutomaton, FiniteAutomaton), '
            f'получили: {type(self)} и {type(other)}'
        )

    if isinstance(self, Regex):
        self, other = Deps.glushkov(self), Deps.glushkov(other)
    if not self.is_deterministic:
        self = Deps.determinize(self)
    if not other.is_deterministic:
        other = Deps.determinize(other)

    # self and other are DFAs by here
    if self.input_symbols != other.input_symbols:
        return False

    for (state_a, state_b) in _get_product_reachable_states(self, other):
        if state_a in self.final_states and state_b not in other.final_states:
            return False

    return True


def _get_product_reachable_states(self: FiniteAutomaton, other: FiniteAutomaton) -> set[str]:
    transitions_a = _simplify_transitions(self.transitions)
    transitions_b = _simplify_transitions(other.transitions)

    product_graph = nx.DiGraph(
        [
            ((start_state_a, start_state_b), (transitions_a[symbol], transitions_b[symbol]))
            for (start_state_a, transitions_a), (start_state_b, transitions_b), symbol in
            product(transitions_a, transitions_b, self.input_symbols,)
        ]
    )

    product_initial_state = (self.initial_state, other.initial_state)
    reachable_states = nx.descendants(product_graph, product_initial_state)
    reachable_states.add(product_initial_state)

    return reachable_states


def _simplify_transitions(transitions: dict[str, dict[str, set[str]]]) -> dict[str, dict[str, str]]:
    return {
        state_from: {
            label: list(states_to)[0] for label, states_to in transitions[state_from].items()
        } for state_from in transitions
    }
