import copy
# from automata.fa.dfa import DFA
import networkx as nx
from models import DFA
from models.base import Type
from pydot import Dot, Edge, Node



class NFA(Type):
    def __init__(
        self,
        *,
        initial_state: str,
        states: set[str],
        final_states: set[str],
        input_symbols: dict,
        transitions: dict[str, dict[str, str]]
    ):
        self.initial_state = initial_state
        self.final_states = final_states.copy()
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.transitions = copy.deepcopy(transitions)


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

    def copy(self):
        return self.__class__(
            states=self.states,
            input_symbols=self.input_symbols,
            transitions=self.transitions,
            initial_state=self.initial_state,
            final_states=self.final_states
        )

    def __or__(self, other):
        if isinstance(other, NFA):
            return self.union(other)
        else:
            raise NotImplementedError

    def __reversed__(self):
        return self.reverse()

    @classmethod
    def from_dfa(cls, dfa):
        nfa_transitions = {}

        for start_state, paths in dfa.transitions.items():
            nfa_transitions[start_state] = {}
            for input_symbol, end_state in paths.items():
                nfa_transitions[start_state][input_symbol] = {end_state}

        return cls(
            states=dfa.states, input_symbols=dfa.input_symbols,
            transitions=nfa_transitions, initial_state=dfa.initial_state,
            final_states=dfa.final_states)

    def _get_next_current_states(self, current_states, input_symbol):
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

    def _get_lambda_closure(self, start_state):
        return self._lambda_closure_dict[start_state]

    def _get_next_current_states2(self, current_states, input_symbol):
        next_current_states = set()

        for current_state in current_states:
            if current_state in self.transitions:
                symbol_end_states = self.transitions[current_state].get(
                    input_symbol)
                if symbol_end_states:
                    next_current_states.update(symbol_end_states)

        return next_current_states

    def _remove_unreachable_states(self):
        reachable_states = self._compute_reachable_states()
        unreachable_states = self.states - reachable_states
        for state in unreachable_states:
            self.states.remove(state)
            del self.transitions[state]
            if state in self.final_states:
                self.final_states.remove(state)

    def _compute_reachable_states(self):
        graph = nx.DiGraph([
            (start_state, end_state)
            for start_state, transition in self.transitions.items()
            for end_states in transition.values()
            for end_state in end_states
        ])
        graph.add_nodes_from(self.states)

        return nx.descendants(graph, self.initial_state) | {self.initial_state}

    def _remove_empty_transitions(self):
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

    def eliminate_lambda(self):
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
            self.transitions[state].pop('', None)

        self._remove_unreachable_states()
        self._remove_empty_transitions()
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

    def determinize(self):
        self.eliminate_lambda()
        return DFA.from_nfa(self)

    def minimize(self):
        return DFA.minify(self.determinize())

    @staticmethod
    def _get_state_maps(state_set_a, state_set_b, *, start=0):

        state_map_a = {
            state: i
            for i, state in enumerate(state_set_a, start=start)
        }

        state_map_b = {
            state: i
            for i, state in enumerate(state_set_b, start=max(state_map_a.values()) + 1)
        }

        return (state_map_a, state_map_b)

    def union(self, other):

        if not isinstance(other, NFA):
            raise NotImplementedError

        # first check superset or subset relation
        if DFA.from_nfa(self).issubset(DFA.from_nfa(other)):
            return other.copy()
        elif DFA.from_nfa(self).issuperset(DFA.from_nfa(other)):
            return self.copy()

        # Starting at 1 because 0 is for the initial state
        (state_map_a, state_map_b) = NFA._get_state_maps(self.states, other.states, start=1)

        new_states = set(state_map_a.values()) | set(state_map_b.values()) | {0}
        new_transitions = {state: dict() for state in new_states}

        # Connect new initial state to both branch
        new_transitions[0] = {'': {state_map_a[self.initial_state], state_map_b[other.initial_state]}}

        # Transitions of self
        NFA._load_new_transition_dict(state_map_a, self.transitions, new_transitions)
        # Transitions of other
        NFA._load_new_transition_dict(state_map_b, other.transitions, new_transitions)

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
            final_states=new_final_states
        )

    def reverse(self):
        new_states = set(self.states)
        new_initial_state = NFA._add_new_state(new_states)

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
            final_states=new_final_states
        )

    @staticmethod
    def _load_new_transition_dict(state_map_dict,
                                  old_transition_dict,
                                  new_transition_dict):


        for state_a, transitions in old_transition_dict.items():
            for symbol, states in transitions.items():
                new_transition_dict[state_map_dict[state_a]][symbol] = {
                    state_map_dict[state_b] for state_b in states
                }

    @staticmethod
    def _add_new_state(state_set, start=0):
        new_state = start
        while new_state in state_set:
            new_state += 1

        state_set.add(new_state)

        return new_state

