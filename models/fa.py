from typing import Optional

from models import Regex
from models.epsilon import EPSILON


class FiniteAutomaton:
    """Данный класс представляет конечный автомат. Пример создания экземпляра (DFA)::
        dfa = FiniteAutomaton(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': {'q0'}, '1': {'q1'}},
                'q1': {'0': {'q0'}, '1': {'q2'}},
                'q2': {'0': {'q2'}, '1': {'q2'}}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
        )
    """

    def __init__(
        self,
        initial_state: str,
        states: set[str],
        final_states: set[str],
        input_symbols: set[str],
        transitions: dict[str, dict[str, set[str]]],
        source_regex: Optional[Regex] = None
    ):
        self.initial_state = initial_state
        self.states = states
        self.final_states = final_states
        self.input_symbols = input_symbols
        self.transitions = transitions
        self.source_regex = source_regex

        self._is_deterministic = all(
            (len(transitions_to) == 1)
            for transition_from in self.transitions
            for transitions_to in self.transitions[transition_from].values()
        ) and EPSILON not in input_symbols

        if not self._is_deterministic and source_regex is None:
            raise ValueError('You must pass the Regex from which the NFA was created')

    @property
    def is_deterministic(self):
        return self._is_deterministic

    @property
    def simplified_transitions(self) -> dict[str, dict[str, str]]:
        """Represent transitions as simple DFA transitions."""
        if not self._is_deterministic:
            raise TypeError('Simplified transitions are available only for DFA.')

        return {
            state_from: {
                label: list(states_to)[0] for label, states_to in
                self.transitions[state_from].items()
            } for state_from in self.transitions
        }
