from typing import Union

import networkx as nx
from itertools import product

from functions import registry
from functions.determinize import determinize
from functions.thompson import Thompson
from models import FiniteAutomaton, Regex
from models.nfa import NFA


@registry.register(registry.FunctionType.PREDICATE)
def subset(self: Union[FiniteAutomaton, Regex], other: Union[FiniteAutomaton, Regex]) -> bool:
    """Проверить, является ли первый НКА/регулярка подмножеством второго НКА/регулярки."""
    if type(self) != type(other) or type(self) not in (FiniteAutomaton, Regex):
        raise ValueError(
            f'Ожидались аргументы типов (Regex, Regex) или (FiniteAutomaton, FiniteAutomaton), '
            f'получили: {type(self)} и {type(other)}'
        )

    if isinstance(self, Regex):
        self = Thompson(self)
    if isinstance(other, Regex):
        other = Thompson(other)
    if not self.is_deterministic:
        self = determinize(self)
    if not other.is_deterministic:
        other = determinize(other)

    # self and other are DFAs by here
    self, other = _unify(self, other)
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
            product(transitions_a, transitions_b, self.input_symbols)
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


def _unify(
    self: FiniteAutomaton, other: FiniteAutomaton
) -> tuple[FiniteAutomaton, FiniteAutomaton]:
    # Do not use on NFAs
    alphabet = {
        symbol
        for automaton in (self, other)
        for state_table in automaton.transitions.values()
        for symbol in state_table.keys()
    }

    TRAP = chr(666)
    for automaton in (self, other):
        automaton.states.add(TRAP)
        for state_from, state_table in automaton.transitions.items():
            for symbol in alphabet:
                if symbol not in state_table:
                    _overwrite_transition(automaton, state_from, symbol, TRAP)
        for symbol in alphabet:
            _overwrite_transition(automaton, TRAP, symbol, TRAP)
            automaton.transitions[TRAP][symbol] = {TRAP}

    return self, other


def _overwrite_transition(self: FiniteAutomaton, state_from: str, symbol: str, state_to: str):
    # Do not use on NFAs
    if state_from in self.transitions:
        self.transitions[state_from][symbol] = {state_to}
    else:
        self.transitions[state_from] = {symbol: {state_to}}
