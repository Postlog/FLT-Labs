import networkx as nx
from itertools import product

import registry
from models import FiniteAutomaton, Regex


class Deps:
    @staticmethod
    def determinize(self: FiniteAutomaton) -> FiniteAutomaton:
        return FiniteAutomaton()

    @staticmethod
    def glushkov(self: Regex) -> FiniteAutomaton:
        return FiniteAutomaton()


@registry.register(registry.FunctionType.PREDICATE)
def subset(self: FiniteAutomaton | Regex, other: FiniteAutomaton | Regex) -> bool:
    """Check if first NFA is a subset of second NFA."""
    if not (
        type(self) == type(other)
        and (isinstance(self, Regex) or isinstance(self, FiniteAutomaton))
    ):
        raise ValueError(
            f'Expected inputs to be (Regex, Regex) or (FiniteAutomaton, FiniteAutomaton), '
            f'got: {type(self)} and {type(other)}'
        )

    if isinstance(self, Regex) and isinstance(other, Regex):
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
    product_graph = nx.DiGraph(
        [
            ((start_state_a, start_state_b), (transitions_a[symbol], transitions_b[symbol]))
            for (start_state_a, transitions_a), (start_state_b, transitions_b), symbol in
            product(
                self.simplified_transitions.items(),
                self.simplified_transitions.items(),
                self.input_symbols,
            )
        ]
    )

    product_initial_state = (self.initial_state, other.initial_state)
    reachable_states = nx.descendants(product_graph, product_initial_state)
    reachable_states.add(product_initial_state)

    return reachable_states
