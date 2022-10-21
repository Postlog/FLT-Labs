from dataclasses import dataclass

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