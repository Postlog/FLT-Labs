from typing import TypeVar

from models import DFA, NFA, Regex


class Deps:
    @staticmethod
    def glushkov(self: Regex) -> NFA:
        return NFA()

    @staticmethod
    def minimize(self: DFA) -> DFA:
        return DFA()

    @staticmethod
    def determinize(self: NFA) -> DFA:
        return DFA()


T = TypeVar('T', NFA, Regex)


def equiv(self: T, other: T) -> bool:
    if isinstance(self, Regex) and isinstance(other, Regex):
        self, other = Deps.glushkov(self), Deps.glushkov(other)

    self, other = Deps.minimize(Deps.determinize(self)), Deps.minimize(Deps.determinize(other))
    return self == other
