from dataclasses import dataclass
from queue import Queue
from typing import Set, Tuple

from models import FiniteAutomaton


@dataclass
class EquivalenceClass:
    """Represents an equivalence class in transition monoid."""

    word: str
    pairs: Set[Tuple[str, str]]


class TransitionMonoid:
    """Represents transition monoid."""

    def __init__(self):
        self.rewriting_rules = {}
        self.classes = []

    @staticmethod
    def _update_candidates(candidates, word, pairs, dfa):
        for letter in dfa.alphabet:
            new_pairs = set()
            for pair in pairs:
                out_state = dfa.transitions.get((pair[1], letter), "")
                if out_state in dfa.useful_states:
                    new_pairs.add((pair[0], out_state))
            candidates.put(EquivalenceClass(word + letter, new_pairs))

    def build(self, dfa: FiniteAutomaton) -> None:
        """Builds a transition monoid according to a given FiniteAutomaton."""
        candidates = Queue()
        self._update_candidates(
            candidates, word="", pairs={(s, s) for s in dfa.useful_states}, dfa=dfa
        )

        while not candidates.empty():
            candidate = candidates.get()
            if all(
                rule_left not in candidate.word for rule_left in self.rewriting_rules
            ):
                same_class = next(
                    (cls for cls in self.classes if cls.pairs == candidate.pairs), None
                )
                if same_class:
                    self.rewriting_rules[candidate.word] = same_class.word
                else:
                    self.classes.append(candidate)
                    self._update_candidates(
                        candidates, word=candidate.word, pairs=candidate.pairs, dfa=dfa
                    )
