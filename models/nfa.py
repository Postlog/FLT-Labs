import copy
from dataclasses import dataclass

from models import DFA
from models.base import Type


@dataclass(frozen=True)
class NFA(Type):
    """Данный класс представляет недетерминированный конечный автомат. Пример создания экземпляра::

            nfa = NFA(
                states={'q0', 'q1', 'q2'},
                input_symbols={'0', '1'},
                transitions={
                    'q0': {'0': ['q0'], '1': ['q1', 'q2']},
                    'q1': {'0': ['q0'], '1': ['q2']},
                    'q2': {'0': ['q2'], '1': ['q2']}
                },
                initial_state='q0',
                final_states={'q0', 'q1'}
            )
    """

    initial_state: str
    states: set[str]
    final_states: set[str]
    input_symbols: set[str]
    transitions: dict[str, dict[str, set[str]]]

