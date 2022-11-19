from dataclasses import dataclass

from models import EPSILON, FiniteAutomaton


@dataclass
class Grammar:
    rules: dict[str, list[list[str]]]
    terminals: set[str]
    nonterminals: set[str]
    start_states: set[str]

    @classmethod
    def from_automaton(
        cls,
        automaton: FiniteAutomaton,
        nonterm_prefix: str,
    ) -> 'Grammar':
        rules, terminals, nonterminals = dict(), set(), set()
        start_states_raw = {nonterm_prefix + automaton.initial_state}

        for state_from, state_transitions in automaton.transitions.items():
            state_from_s = nonterm_prefix + state_from
            nonterminals.add(state_from_s)
            for symbol, states_to in state_transitions.items():
                if not (symbol == '' or symbol == EPSILON):
                    terminals.add(symbol)
                if state_from_s not in rules:
                    rules[state_from_s] = []

                for state_to in states_to:
                    state_to_s = nonterm_prefix + state_to
                    nonterminals.add(state_to_s)
                    if symbol == '' or symbol == EPSILON:
                        rules[state_from_s].append([state_to_s])
                    else:
                        rules[state_from_s].append([symbol, state_to_s])

            for state in automaton.states:
                state_s = nonterm_prefix + state
                if state in automaton.final_states and state_s not in rules:
                    rules[state_s] = [[]]

        return cls(
            rules,
            terminals,
            nonterminals,
            start_states_raw
        )

    @classmethod
    def from_automaton_reversed(
        cls,
        automaton: FiniteAutomaton,
        nonterm_prefix: str,
    ):
        rules, terminals, nonterminals = dict(), set(), set()
        start_states_raw = {nonterm_prefix + automaton.initial_state}

        for state_from, state_transitions in automaton.transitions.items():
            state_from_s = nonterm_prefix + state_from
            if state_from_s in start_states_raw:
                rules[state_from_s] = [[]]
            terminals.add(state_from_s)

            for symbol, states_to in state_transitions.items():
                if not (symbol == '' or symbol == EPSILON):
                    terminals.add(symbol)
                for state_to in states_to:
                    state_to_s = nonterm_prefix + state_to
                    if state_to_s not in rules:
                        rules[state_to_s] = []
                    nonterminals.add(state_to_s)
                    if symbol == '' or symbol == EPSILON:
                        rules[state_to_s].append([state_from_s])
                    else:
                        rules[state_to_s].append([symbol, state_from_s])

        return cls(
            rules,
            terminals,
            nonterminals,
            start_states_raw
        )

    def is_bisimilar(self, other: 'Grammar'):
        if not isinstance(other, Grammar):
            raise TypeError(f'Ожидался тип Grammar, получили: {type(other)}')

        if sorted(self.terminals) != sorted(other.terminals):
            return False, None, None, None

        rules1, nonterms1, classes1, _ = division_into_equivalence_classes(
            self.rules,
            list(self.nonterminals)
        )
        rules2, nonterms2, classes2, _ = division_into_equivalence_classes(
            other.rules,
            list(other.nonterminals)
        )
        if len(nonterms1) != len(nonterms2) or len(rules1) != len(rules2):
            return False, None, None, None

        rules, nonterms = grammar_union(rules1, rules2, nonterms1, nonterms2)
        rules, nonterms, classes, nonterm_class_num = division_into_equivalence_classes(
            rules,
            nonterms
        )
        if len(classes) != len(classes1):
            return False, None, None, None  # , classes1, classes2

        union_classes = classes_union(classes1, classes2, classes)
        for i in range(len(self.start_states)):
            key = False
            class_num_1 = banana(list(self.start_states)[i], union_classes)
            for j in range(len(other.start_states)):
                class_num_2 = banana(list(other.start_states)[j], union_classes)
                if class_num_1 == class_num_2:
                    key = True
            if not key:
                return False, None, None, None

        return True, classes1, classes2, union_classes


def division_into_equivalence_classes(
    input_rules: dict[str, list[list[str]]],
    nonterms: list[str],
):
    rules: dict[str, list[list[str]]] = {}
    classes: dict[str, int | None] = {}
    empty_nonterms: list[str] = []

    for key in input_rules:
        if len(input_rules[key][0]) != 0:
            rules[key] = input_rules[key]
        else:
            empty_nonterms.append(key)

    for key in nonterms:
        classes[key] = None
    classes, equiv_classes = split_classes(rules, classes, nonterms)

    old_size = len(equiv_classes)
    while True:
        classes, equiv_classes = split_classes(rules, classes, nonterms)
        if old_size == len(equiv_classes):
            break
        old_size = len(equiv_classes)

    rules, nonterms, equiv_classes = new_grammar(
        rules,
        empty_nonterms,
        nonterms,
        equiv_classes,
        classes
    )
    return rules, nonterms, equiv_classes, classes


def new_grammar(
    rules: dict[str, list[list[str]]],
    empty_nonterms: list[str],
    nonterms: list[str],
    equiv_classes: list[list[str]],
    classes: dict[str, int | None]
):
    new_rules, new_terms, new_nonterms = {}, [], []
    empty_nonterm = empty_nonterms[0] if len(empty_nonterms) > 0 else None

    for eq_nonterms in equiv_classes:
        nonterm = eq_nonterms[0]
        new_rules[nonterm] = []
        for i in range(len(rules[nonterm])):
            new_rules[nonterm].append([[]] * len(rules[nonterm][i]))
            for j in range(len(rules[nonterm][i])):
                symbol = rules[nonterm][i][j]
                if symbol in nonterms:
                    if classes[symbol] == None:
                        new_rules[nonterm][i][j] = empty_nonterm
                    else:
                        new_rules[nonterm][i][j] = equiv_classes[classes[symbol]][0]
                else:
                    new_rules[nonterm][i][j] = symbol

    if len(empty_nonterms) > 0:
        new_rules[empty_nonterm] = [[]]
        equiv_classes.append(list(empty_nonterms))

    new_nonterms = list(new_rules.keys())

    return new_rules, new_nonterms, equiv_classes


def split_classes(
    rules: dict[str, list[list[str]]],
    classes: dict[str, int | None],
    nonterms: list[str]
):
    new_rules = dict()
    nonterm_classes = dict()

    for key in rules:
        words = []
        for i in range(len(rules[key])):
            word = ''
            for j in range(len(rules[key][i])):
                symbol = rules[key][i][j]
                if symbol in nonterms:
                    word += str(classes[symbol])
                else:
                    word += symbol
            words.append(word)
        words = tuple(words)
        if words in new_rules:
            nonterm_classes[words].append(key)
        else:
            nonterm_classes[words] = [key]
            new_rules[words] = key

    equiv_classes = []
    index = 0
    for key in nonterm_classes:
        equiv_classes.append(nonterm_classes[key])
        for i in range(len(nonterm_classes[key])):
            classes[nonterm_classes[key][i]] = index
        index += 1

    return classes, equiv_classes


def grammar_union(
    rules1: dict[str, list[list[str]]],
    rules2: dict[str, list[list[str]]],
    nonterms1: list[str],
    nonterms2: list[str],
):
    for nonterm in rules2.keys():
        rules1[nonterm] = list(rules2[nonterm])
    return rules1, list(set(nonterms1) | set(nonterms2))


def classes_union(classes1: list[list[str]], classes2, classes):
    state_prefix_1 = classes1[0][0][0]  # 000 lol
    new_equiv_classes = []
    for klass in classes:
        new_equiv_classes.append([])
        for j in range(len(klass)):
            if klass[j][0] == state_prefix_1:
                equiv_class_1 = apple(classes1, klass[j])
                new_equiv_classes[-1] += equiv_class_1
            else:
                equiv_class_2 = apple(classes2, klass[j])
                new_equiv_classes[-1] += equiv_class_2
    return new_equiv_classes


def apple(classes, val):
    for klass in classes:
        for v in klass:
            if v == val:
                return klass


def banana(nonterm, klass):
    for i, val in enumerate(klass):
        for j, v in enumerate(val):
            if klass[i][j] == nonterm:
                return i

