import copy

from models.base import Type


class DFA(Type):
    def __init__(
        self,
        *,
        initial_state: str,
        final_states: set[str],
        states: set[str],
        input_symbols: dict,
        transitions: dict[str, dict[str, str]]
    ):
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)