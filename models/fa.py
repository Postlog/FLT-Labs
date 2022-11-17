import typing
import networkx as nx
from models import Regex
from models.epsilon import EPSILON
from itertools import product
from collections import deque



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


        lambda_graph = nx.DiGraph()
        lambda_graph.add_nodes_from(self.states)
        lambda_graph.add_edges_from([
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for char, end_states in transition.items()
            for end_state in end_states
            if char == ''
        ])

        self._lambda_closure_dict = {
            state: nx.descendants(lambda_graph, state) | {state}
            for state in self.states
        }

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


    def copy(self):
        """Create a deep copy of the NFA. Overrides copy in base class due to extra parameter."""
        return self.__class__(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=self.final_states,
            source_regex=self.source_regex
        )

    # """Return the union of this NFA and another NFA."""
    def __or__(self, other):

        if isinstance(other, FiniteAutomaton):
            if self._is_deterministic and other._is_deterministic:
                return self.union_for_dfa(other)
            if not self._is_deterministic and not other._is_deterministic:
                return self.union_for_nfa(other)
            else:
                raise
        else:
            raise NotImplementedError


    def __reversed__(self):
        if self._is_deterministic == False:
            return self.reverse()
        else:
            raise


    # Return the next set of current states given the current set.
    def _get_next_current_states(self, current_states, input_symbol):
        if self._is_deterministic == False:
            next_current_states = set()
            for current_state in current_states:
                if current_state in self.transitions:
                    symbol_end_states = self.transitions[current_state].get(
                        input_symbol)
                    if symbol_end_states:
                        for end_state in symbol_end_states:
                            next_current_states.update(
                                self._lambda_closure_dict[end_state])

            return next_current_states
        else:
            raise

    def _get_lambda_closure(self, start_state):
        """
        Return the lambda closure for the given state.

        The lambda closure of a state q is the set containing q, along with
        every state that can be reached from q by following only lambda
        transitions.
        """
        if self._is_deterministic == False:
            return self._lambda_closure_dict[start_state]
        else:
            raise

    def _get_next_current_states2(self, current_states, input_symbol):
        """Return the next set of current states given the current set."""
        if self._is_deterministic == False:
            next_current_states = set()
            for current_state in current_states:
                if current_state in self.transitions:
                    symbol_end_states = self.transitions[current_state].get(
                        input_symbol)
                    if symbol_end_states:
                        next_current_states.update(symbol_end_states)
            return next_current_states
        else:
            raise

    def _remove_unreachable_states_for_nfa(self):
        if self._is_deterministic == False:
            """Remove states which are not reachable from the initial state."""
            reachable_states = self._compute_reachable_states_for_nfa()
            unreachable_states = self.states - reachable_states
            for state in unreachable_states:
                self.states.remove(state)
                del self.transitions[state]
                if state in self.final_states:
                    self.final_states.remove(state)
        else:
            raise

    def _compute_reachable_states_for_nfa(self):
        if self._is_deterministic == False:
            """Compute the states which are reachable from the initial state."""
            graph = nx.DiGraph([
                (start_state, end_state)
                for start_state, transition in self.transitions.items()
                for end_states in transition.values()
                for end_state in end_states
            ])
            graph.add_nodes_from(self.states)
            return nx.descendants(graph, self.initial_state) | {self.initial_state}
        else:
            raise

    def _remove_empty_transitions(self):
        if self._is_deterministic == False:

            """Deletes transitions to empty set of states"""
            to_delete_sym = {}
            for state in self.transitions.keys():
                for input_symbol, to_states in self.transitions[state].items():
                    if to_states == set():
                        if state in to_delete_sym:
                            to_delete_sym[state].add(input_symbol)
                        else:
                            to_delete_sym[state] = {input_symbol}

            for state, input_symbols in to_delete_sym.items():
                for input_symbol in input_symbols:
                    del self.transitions[state][input_symbol]

            for state in list(self.transitions.keys()):
                if self.transitions[state] == dict():
                    del self.transitions[state]
        else:
            raise

    def eliminate_lambda(self):
        if self._is_deterministic == False:
            """Removes epsilon transitions from the NFA which recognizes the same language."""
            for state in self.states:
                lambda_enclosure = self._lambda_closure_dict[state] - {state}
                for input_symbol in self.input_symbols:
                    next_current_states = self._get_next_current_states2(lambda_enclosure, input_symbol)
                    if state not in self.transitions:
                        self.transitions[state] = dict()
                    if input_symbol in self.transitions[state]:
                        self.transitions[state][input_symbol].update(next_current_states)
                    else:
                        self.transitions[state][input_symbol] = next_current_states

                if state not in self.final_states and self.final_states & lambda_enclosure:
                    self.final_states.add(state)
                self.transitions[state].pop(EPSILON, None)

            self._remove_unreachable_states_for_nfa()
            self._remove_empty_transitions()
            lambda_graph = nx.DiGraph()
            lambda_graph.add_nodes_from(self.states)
            lambda_graph.add_edges_from([
                (start_state, end_state)
                for start_state, transition in self.transitions.items()
                for char, end_states in transition.items()
                for end_state in end_states
                if char == EPSILON
            ])

            self._lambda_closure_dict = {
                state: nx.descendants(lambda_graph, state) | {state}
                for state in self.states
            }
        else:
            raise


    def determinize(self):
        if self._is_deterministic == False:
            self.eliminate_lambda()
            return FiniteAutomaton.from_nfa(self)
        else:
            raise NotImplementedError
    def minimize(self):
        if self._is_deterministic == False:
            return FiniteAutomaton.minify(self.determinize())
        else:
            raise NotImplementedError



    @staticmethod
    def _get_state_maps(state_set_a, state_set_b, *, start=0):
        """
        Generate state map dicts from given sets. Useful when the state set has
        to be a union of the state sets of component FAs.
        """

        state_map_a = {
            state: i
            for i, state in enumerate(state_set_a, start=start)
        }

        state_map_b = {
            state: i
            for i, state in enumerate(state_set_b, start=max(state_map_a.values()) + 1)
        }

        return (state_map_a, state_map_b)

    def union_for_nfa(self, other):
        if self._is_deterministic == False:
            """
            Given two NFAs, M1 and M2, which accept the languages
            L1 and L2 respectively, returns an NFA which accepts
            the union of L1 and L2.
            """
            if not isinstance(other, FiniteAutomaton):
                raise NotImplementedError

            # first check superset or subset relation
            if FiniteAutomaton.determinize(self).issubset(FiniteAutomaton.determinize(other)):
                return other.copy()
            elif FiniteAutomaton.determinize(self).issuperset(FiniteAutomaton.determinize(other)):
                return self.copy()

            # Starting at 1 because 0 is for the initial state
            (state_map_a, state_map_b) = FiniteAutomaton._get_state_maps(self.states, other.states, start=1)

            new_states = set(state_map_a.values()) | set(state_map_b.values()) | {0}
            new_transitions = {state: dict() for state in new_states}

            # Connect new initial state to both branch
            new_transitions[0] = {'': {state_map_a[self.initial_state], state_map_b[other.initial_state]}}

            # Transitions of self
            FiniteAutomaton._load_new_transition_dict(state_map_a, self.transitions, new_transitions)
            # Transitions of other
            FiniteAutomaton._load_new_transition_dict(state_map_b, other.transitions, new_transitions)

            # Final states
            new_final_states = (
                {state_map_a[state] for state in self.final_states}
                | {state_map_b[state] for state in other.final_states}
            )

            return self.__class__(
                states=new_states,
                input_symbols=self.input_symbols | other.input_symbols,
                transitions=new_transitions,
                initial_state=0,
                final_states=new_final_states,
                source_regex=self.source_regex
            )
        else:
            raise

    def reverse(self):
        if self._is_deterministic == False:
            """
            Given an NFA which accepts the language L this function
            returns an NFA which accepts the reverse of L.
            """
            new_states = set(self.states)
            new_initial_state = FiniteAutomaton._add_new_state(new_states)

            # Transitions are the same except reversed
            new_transitions = dict()
            for state in new_states:
                new_transitions[state] = dict()
            for state_a, transitions in self.transitions.items():
                for symbol, states in transitions.items():
                    for state_b in states:
                        if symbol not in new_transitions[state_b]:
                            new_transitions[state_b][symbol] = set()
                        new_transitions[state_b][symbol].add(state_a)
            new_transitions[new_initial_state][''] = set()
            # And we additionally have epsilon transitions from
            # new initial state to each old final state.
            for state in self.final_states:
                new_transitions[new_initial_state][''].add(state)

            new_final_states = {self.initial_state}

            return self.__class__(
                states=new_states,
                input_symbols=self.input_symbols,
                transitions=new_transitions,
                initial_state=new_initial_state,
                final_states=new_final_states,
                source_regex=self.source_regex
            )
        else:
            raise

    @staticmethod
    def _load_new_transition_dict(state_map_dict,
                                  old_transition_dict,
                                  new_transition_dict):
        """
        Load the new_transition_dict with the old transitions corresponding to
        the given state_map_dict.
        """

        for state_a, transitions in old_transition_dict.items():
            for symbol, states in transitions.items():
                new_transition_dict[state_map_dict[state_a]][symbol] = {
                    state_map_dict[state_b] for state_b in states
                }

    @staticmethod
    def _add_new_state(state_set, start=0):
        """Adds new state to the state set and returns it"""
        new_state = start
        while new_state in state_set:
            new_state += 1

        state_set.add(new_state)

        return new_state



    def __sub__(self, other):
        if self._is_deterministic == True:
            """Return a DFA that is the difference of this DFA and another DFA."""
            if isinstance(other, FiniteAutomaton):
                return self.difference(other)
            else:
                raise NotImplementedError
        else:
            raise

    def __xor__(self, other):
        if self._is_deterministic == True:
            """Return the symmetric difference of this DFA and another DFA."""
            if isinstance(other, FiniteAutomaton):
                return self.symmetric_difference(other)
            else:
                raise NotImplementedError
        else:
            raise


    def __and__(self, other):
        if self._is_deterministic == True:
            """Return the intersection of this DFA and another DFA."""
            if isinstance(other, FiniteAutomaton):
                return self.intersection(other)
            else:
                raise NotImplementedError
        else:
            raise

    def __invert__(self):
        if self._is_deterministic == True:
            """Return the complement of this DFA and another DFA."""
            return self.complement()

    def minify(self, retain_names=True):
        if self._is_deterministic == True:
            """
            Create a minimal DFA which accepts the same inputs as this DFA.
    
            First, non-reachable states are removed.
            Then, similiar states are merged using Hopcroft's Algorithm.
                retain_names: If True, merged states retain names.
                              If False, new states will be named 0, ..., n-1.
            """
            new_dfa = self.copy()
            new_dfa._remove_unreachable_states()
            new_dfa._merge_states(retain_names=retain_names)
            return new_dfa
        else:
            raise

    def _get_digraph(self) -> nx.DiGraph:
        if self._is_deterministic == True:
            """Return a digraph corresponding to this DFA with transition symbols ignored"""
            return nx.DiGraph([
                (start_state, end_state)
                for start_state, transition in self.transitions.items()
                for end_state in transition.values()
            ])
        else:
            raise

    def _compute_reachable_states(self):
        if self._is_deterministic == True:
            """Compute the states which are reachable from the initial state."""
            G = self._get_digraph()
            return nx.descendants(G, self.initial_state) | {self.initial_state}
        else:
            raise

    def _remove_unreachable_states(self):
        if self._is_deterministic == True:
            """Remove states which are not reachable from the initial state."""
            reachable_states = self._compute_reachable_states()
            unreachable_states = self.states - reachable_states
            for state in unreachable_states:
                self.states.remove(state)
                del self.transitions[state]
                if state in self.final_states:
                    self.final_states.remove(state)
        else:
            raise

    def _merge_states(self, retain_names=False):
        if self._is_deterministic == True:
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
                    return list(eq)[0] if len(eq) == 1 else FiniteAutomaton._stringify_states(eq)

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
        else:
            raise

    def _cross_product(self, other):
        if self._is_deterministic == True:
            """
            Creates a new DFA which is the cross product of DFAs self and other
            with an empty set of final states.
            """

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
                final_states=set(),
                source_regex=self.source_regex
            )
        else:
            raise

    def union_for_dfa(self, other, *, retain_names=False, minify=True):
        if self._is_deterministic == True:
            """
            Takes as input two DFAs M1 and M2 which
            accept languages L1 and L2 respectively.
            Returns a DFA which accepts the union of L1 and L2.
            """
            new_dfa = self._cross_product(other)

            new_dfa.final_states = {
                self._stringify_states_unsorted((state_a, state_b))
                for state_a, state_b in product(self.states, other.states)
                if (state_a in self.final_states or state_b in other.final_states)
            }

            if minify:
                return new_dfa.minify(retain_names=retain_names)
            return new_dfa
        else:
            raise

    def intersection(self, other, *, retain_names=False, minify=True):
        """
        Takes as input two DFAs M1 and M2 which
        accept languages L1 and L2 respectively.
        Returns a DFA which accepts the intersection of L1 and L2.
        """
        new_dfa = self._cross_product(other)

        new_dfa.final_states = {
            self._stringify_states_unsorted((state_a, state_b))
            for state_a, state_b in product(self.final_states, other.final_states)
        }

        if minify:
            return new_dfa.minify(retain_names=retain_names)
        return new_dfa

    def difference(self, other, *, retain_names=False, minify=True):
        if self._is_deterministic == True:
            """
            Takes as input two DFAs M1 and M2 which
            accept languages L1 and L2 respectively.
            Returns a DFA which accepts the difference of L1 and L2.
            """
            new_dfa = self._cross_product(other)

            new_dfa.final_states = {
                self._stringify_states_unsorted((state_a, state_b))
                for state_a, state_b in product(self.final_states, other.states - other.final_states)
            }

            if minify:
                return new_dfa.minify(retain_names=retain_names)
            return new_dfa
        else:
            raise

    def symmetric_difference(self, other, *, retain_names=False, minify=True):
        if self._is_deterministic == True:
            """
            Takes as input two DFAs M1 and M2 which
            accept languages L1 and L2 respectively.
            Returns a DFA which accepts the symmetric difference of L1 and L2.
            """
            new_dfa = self._cross_product(other)
            new_dfa.final_states = {
                self._stringify_states_unsorted((state_a, state_b))
                for state_a, state_b in product(self.states, other.states)
                if (state_a in self.final_states) ^ (state_b in other.final_states)
            }

            if minify:
                return new_dfa.minify(retain_names=retain_names)
            return new_dfa
        else:
            raise

    def complement(self):
        if self._is_deterministic == True:
            """Return the complement of this DFA."""
            new_dfa = self.copy()
            new_dfa.final_states ^= self.states
            return new_dfa
        else:
            raise

    @staticmethod
    def _stringify_states_unsorted(states):
        """Stringify the given set of states as a single state name."""
        return '{{{}}}'.format(','.join(states))

    @staticmethod
    def _stringify_states(states):
        """Stringify the given set of states as a single state name."""
        return '{{{}}}'.format(','.join(sorted(str(state) for state in states)))

    @classmethod
    def from_nfa(cls, target_nfa):
        """Initialize this DFA as one equivalent to the given NFA."""
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
            final_states=dfa_final_states, source_regex=target_nfa.source_regex)








class FiniteAutomatonIndexed(FiniteAutomaton):
    start_number: int
    end_number: int

    def __init__(
        self,
        initial_state: str,
        states: set[str],
        final_states: set[str],
        input_symbols: set[str],
        transitions: dict[str, dict[str, set[str]]],
        start_number: int,
        end_number: int,
        source_regex: typing.Optional[Regex] = None
    ):
        super().__init__(
            initial_state,
            states,
            final_states,
            input_symbols,
            transitions,
            source_regex
        )
        self.start_number = start_number
        self.end_number = end_number

    def add_state(self, pos):
        self.states.add('q' + str(pos))


if __name__ == "__main__":
    nfa = FiniteAutomaton(
        #тест для детерминизации
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b', EPSILON},
        transitions={
            'q0': {'b': {'q3'}, 'a': {'q1'}, EPSILON: {'q2'}},
            'q1': {EPSILON: {'q3'}},
            'q2': {'b': {'q1'}},
            'q3': {'a': {'q1'}, EPSILON: {'q2'}}
        },
        initial_state='q0',
        final_states={'q3'},
        source_regex= ''


        #тест для минимизации
        # states={'s0', 's1', 's2', 's3', 's4', 's5'},
        # input_symbols={'0', '1'},
        # transitions={
        #     's0': {'0': {'s0'}, '1': {'s1'}},
        #     's1': {'0': {'s2'}, '1': {'s1'}},
        #     's2': {'0': {'s0'}, '1': {'s3'}},
        #     's3': {'0': {'s4'}, '1': {'s3'}},
        #     's4': {'0': {'s5'}, '1': {'s3'}},
        #     's5': {'0': {'s5'}, '1': {'s3'}}
        # },
        # initial_state='s0',
        # final_states={'s3', 's4', 's5'}
    )


    check = FiniteAutomaton.determinize(nfa)
    # check = NFA.minimize(nfa)
    a = 1