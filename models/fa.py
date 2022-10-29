import typing

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
        source_regex: typing.Optional[Regex] = None
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
            raise ValueError('Нужно указать объект Regex из которого НКА был создан')

    @property
    def is_deterministic(self):
        return self._is_deterministic

    def prefix(self, length: int, state: typing.Optional[str] = None) -> set[str]:
        if not self.is_deterministic:
            raise TypeError('Невозможно посчитать префикс для НКА')

        if length <= 0:
            return set()

        if state is None:
            state = self.initial_state

        prefixes: set[str] = set()
        for symbol in self.input_symbols:
            next_states = self._get_transitions(state, symbol)

            if len(next_states) == 0:
                continue

            next_prefixes = self.prefix(length - 1, next_states[0])
            if len(next_prefixes) > 0:
                for next_prefix in next_prefixes:
                    prefixes.add(symbol + next_prefix)
            else:
                prefixes.add(symbol)

        return prefixes

    def _get_transitions(self, from_state: str, symbol: str) -> list[str]:
        return list(self.transitions.get(from_state, {}).get(symbol, set()))
