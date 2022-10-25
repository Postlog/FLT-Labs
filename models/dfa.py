from dataclasses import dataclass
import typing

from models.base import Type


@dataclass(frozen=True)
class DFA(Type):
    """Данный класс представляет детерминированный конечный автомат. Пример создания экземпляра::

    dfa = DFA(
            states={'q0', 'q1', 'q2'},
            input_symbols={'0', '1'},
            transitions={
                'q0': {'0': 'q0', '1': 'q1'},
                'q1': {'0': 'q0', '1': 'q2'},
                'q2': {'0': 'q2', '1': 'q2'}
            },
            initial_state='q0',
            final_states={'q0', 'q1'}
    )
    """

    initial_state: str
    final_states: set[str]
    states: set[str]
    input_symbols: set[str]
    transitions: dict[str, dict[str, str]]

    def get_transition(self, from_state: str, symbol: str) -> typing.Optional[str]:
        return self.transitions.get(from_state, {}).get(symbol, None)

    def prefix(self, length: int, state: str = None) -> set[str]:
        if length <= 0:
            return set()

        if state is None:
            state = self.initial_state

        prefixes: set[str] = set()
        for symbol in self.input_symbols:
            next_state = self.get_transition(state, symbol)

            if next_state is None:
                continue

            next_prefixes = self.prefix(length - 1, next_state)
            if len(next_prefixes) > 0:
                for next_prefix in next_prefixes:
                    prefixes.add(symbol + next_prefix)
            else:
                prefixes.add(symbol)

        return prefixes
