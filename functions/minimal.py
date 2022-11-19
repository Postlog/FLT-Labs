from typing import Optional

from functions.minimize import minimize
from functions.pump_length import pump_length
from models import FiniteAutomaton, Int, NullableBool, Regex


def minimal(self: FiniteAutomaton) -> NullableBool:
    if self.is_deterministic:
        is_minimal = len(self.states) == len(minimize(self).states)
        return NullableBool(is_minimal)

    if len(self.states) > len(self.source_regex.source_str):
        return NullableBool(False)

    minimal_previous_length = 10 ** 10
    for previous_fa in FiniteAutomaton.MEMORY[self.source_regex.source_str]:
        minimal_previous_length = min(minimal_previous_length, len(previous_fa.states))
    if len(self.states) > minimal_previous_length:
        return NullableBool(False)

    states_with_transitions_count = 0
    for state in self.states:
        if state in self.transitions and len(self.transitions[state]) > 0:
            states_with_transitions_count += 1
    if states_with_transitions_count == pump_length(self.source_regex):
        return NullableBool(True)

    return NullableBool(None)
