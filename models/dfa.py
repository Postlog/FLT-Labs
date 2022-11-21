import copy

from models.base import Type
import networkx as nx
from itertools import product
from collections import deque


class DFA(Type):
    def __init__(
        self,
        *,
        initial_state: str,
        states: set[str],
        final_states: set[str],
        input_symbols: set[str],
        transitions: dict[str, dict[str, set[str]]]
    ):
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)

    def copy(self):
        return self.__class__(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=self.final_states
        )

    def __sub__(self, other):
        if isinstance(other, DFA):
            return self.difference(other)
        else:
            raise NotImplementedError

    def __xor__(self, other):
        if isinstance(other, DFA):
            return self.symmetric_difference(other)
        else:
            raise NotImplementedError

    def __or__(self, other):
        if isinstance(other, DFA):
            return self.union(other)
        else:
            raise NotImplementedError

    def __and__(self, other):
        if isinstance(other, DFA):
            return self.intersection(other)
        else:
            raise NotImplementedError

    def __invert__(self):
        return self.complement()

    def minify(self, retain_names=True):

        new_dfa = self.copy()
        new_dfa._remove_unreachable_states()
        new_dfa._merge_states(retain_names=retain_names)
        return new_dfa

    def _get_digraph(self) -> nx.DiGraph:
        return nx.DiGraph([
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for end_state in transition.values()
        ])

    def _compute_reachable_states(self):
        G = self._get_digraph()
        return nx.descendants(G, self.initial_state) | {self.initial_state}

    def _remove_unreachable_states(self):
        reachable_states = self._compute_reachable_states()
        unreachable_states = self.states - reachable_states
        for state in unreachable_states:
            self.states.remove(state)
            del self.transitions[state]
            if state in self.final_states:
                self.final_states.remove(state)

    def _merge_states(self, retain_names=False):
        eq_classes = []
        if len(self.final_states) != 0:
            eq_classes.append(frozenset(self.final_states))
        if len(self.final_states) != len(self.states):
            eq_classes.append(
                frozenset(set(self.states).difference(self.final_states))
            )
        eq_classes = set(eq_classes)

        processing = set([frozenset(self.final_states)])

        while len(processing) > 0:
            active_state = processing.pop()
            for active_letter in self.input_symbols:
                states_that_move_into_active_state = frozenset(
                    state
                    for state in self.states
                    if self.transitions[state][active_letter] in active_state
                )

                copy_eq_classes = set(eq_classes)

                for checking_set in copy_eq_classes:
                    XintY = checking_set.intersection(
                        states_that_move_into_active_state
                    )
                    if len(XintY) == 0:
                        continue
                    XdiffY = checking_set.difference(
                        states_that_move_into_active_state
                    )
                    if len(XdiffY) == 0:
                        continue
                    eq_classes.remove(checking_set)
                    eq_classes.add(XintY)
                    eq_classes.add(XdiffY)
                    if checking_set in processing:
                        processing.remove(checking_set)
                        processing.add(XintY)
                        processing.add(XdiffY)
                    else:
                        if len(XintY) < len(XdiffY):
                            processing.add(XintY)
                        else:
                            processing.add(XdiffY)

        def get_name(eq, i):
            if retain_names:
                return list(eq)[0] if len(eq) == 1 else DFA._stringify_states(eq)

            return str(i)

        # now eq_classes are good to go, make them a list for ordering
        eq_class_name_pairs = [
            (eq, get_name(eq, i))
            for i, eq in enumerate(eq_classes)
        ]

        # need a backmap to prevent constant calls to index
        back_map = {
            state: name
            for eq, name in eq_class_name_pairs
            for state in eq
        }

        new_input_symbols = self.input_symbols
        new_states = set(back_map.values())
        new_initial_state = back_map[self.initial_state]
        new_final_states = {back_map[acc] for acc in self.final_states}
        new_transitions = {
            name: {
                letter: back_map[self.transitions[list(eq)[0]][letter]]
                for letter in self.input_symbols
            }
            for eq, name in eq_class_name_pairs
        }

        self.states = new_states
        self.input_symbols = new_input_symbols
        self.transitions = new_transitions
        self.initial_state = new_initial_state
        self.final_states = new_final_states

    def _cross_product(self, other):


        new_states = {
            self._stringify_states_unsorted((a, b))
            for (a, b) in product(self.states, other.states)
        }

        new_transitions = {
            self._stringify_states_unsorted((state_a, state_b)): {
                symbol: self._stringify_states_unsorted((transitions_a[symbol], transitions_b[symbol]))
                for symbol in self.input_symbols
            }
            for (state_a, transitions_a), (state_b, transitions_b) in
            product(self.transitions.items(), other.transitions.items())
        }

        new_initial_state = self._stringify_states_unsorted(
            (self.initial_state, other.initial_state)
        )

        return self.__class__(
            states=new_states,
            input_symbols=self.input_symbols,
            transitions=new_transitions,
            initial_state=new_initial_state,
            final_states=set()
        )

    def union(self, other, *, retain_names=False, minify=True):

        new_dfa = self._cross_product(other)

        new_dfa.final_states = {
            self._stringify_states_unsorted((state_a, state_b))
            for state_a, state_b in product(self.states, other.states)
            if (state_a in self.final_states or state_b in other.final_states)
        }

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def intersection(self, other, *, retain_names=False, minify=True):

        new_dfa = self._cross_product(other)

        new_dfa.final_states = {
            self._stringify_states_unsorted((state_a, state_b))
            for state_a, state_b in product(self.final_states, other.final_states)
        }

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def difference(self, other, *, retain_names=False, minify=True):

        new_dfa = self._cross_product(other)

        new_dfa.final_states = {
            self._stringify_states_unsorted((state_a, state_b))
            for state_a, state_b in product(self.final_states, other.states - other.final_states)
        }

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def symmetric_difference(self, other, *, retain_names=False, minify=True):

        new_dfa = self._cross_product(other)
        new_dfa.final_states = {
            self._stringify_states_unsorted((state_a, state_b))
            for state_a, state_b in product(self.states, other.states)
            if (state_a in self.final_states) ^ (state_b in other.final_states)
        }

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def complement(self):
        new_dfa = self.copy()
        new_dfa.final_states ^= self.states
        return new_dfa

    @staticmethod
    def _stringify_states_unsorted(states):
        return '{{{}}}'.format(','.join(states))

    @staticmethod
    def _stringify_states(states):
        return '{{{}}}'.format(','.join(sorted(str(state) for state in states)))

    @classmethod
    def from_nfa(cls, target_nfa):
        dfa_states = set()
        dfa_symbols = target_nfa.input_symbols
        dfa_transitions = dict()

        # equivalent DFA states states
        nfa_initial_states = target_nfa._get_lambda_closure(target_nfa.initial_state)
        dfa_initial_state = cls._stringify_states(nfa_initial_states)
        dfa_final_states = set()

        state_queue = deque()
        state_queue.append(nfa_initial_states)
        while state_queue:
            current_states = state_queue.popleft()
            current_state_name = cls._stringify_states(current_states)
            if current_state_name in dfa_states:
                # We've been here before and nothing should have changed.
                continue

            # Add NFA states to DFA as it is constructed from NFA.
            dfa_states.add(current_state_name)
            dfa_transitions[current_state_name] = {}
            if (current_states & target_nfa.final_states):
                dfa_final_states.add(current_state_name)

            # Enqueue the next set of current states for the generated DFA.
            for input_symbol in target_nfa.input_symbols:
                next_current_states = target_nfa._get_next_current_states(
                    current_states, input_symbol)
                dfa_transitions[current_state_name][input_symbol] = cls._stringify_states(next_current_states)
                state_queue.append(next_current_states)

        return cls(
            states=dfa_states, input_symbols=dfa_symbols,
            transitions=dfa_transitions, initial_state=dfa_initial_state,
            final_states=dfa_final_states)