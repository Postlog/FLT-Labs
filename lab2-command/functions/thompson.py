'''Модуль преобразования регулярного выражения в автомат Томпсона'''

from models.regex import Regex, Node
from models import FiniteAutomaton, FiniteAutomatonIndexed, EPSILON
import functions.registry as registry

"""
Переход на первую ветку, добавление состояния
и eps перехода к нему
"""


def __switching_to_fst_branch_if_alt(pos: int, finite_automata: FiniteAutomatonIndexed) -> tuple[str, FiniteAutomatonIndexed]:
    finite_automata.add_state(pos + 1)
    alt_pos = 'q' + str(pos)
    finite_automata.transitions[alt_pos] = {
        EPSILON: {'q' + str(pos + 1)}
    }
    finite_automata.start_number += 1
    finite_automata.end_number += 1
    return alt_pos, finite_automata


def __add_alt_final_states(pos_f: int, fa2: FiniteAutomatonIndexed):
    fa2.add_state(fa2.end_number + 1)

    """
    Объявление последних состояний каждой ветки
    финальными перед соединением
    """
    fa2.final_states.add('q' + str(pos_f))
    fa2.final_states.add('q' + str(fa2.end_number))

    ''' соединеие eps переходами '''
    fa2.transitions['q' + str(pos_f)] = {
        EPSILON: {'q' + str(fa2.end_number + 1)}
    }

    fa2.transitions['q' + str(fa2.end_number)] = {
        EPSILON: {'q' + str(fa2.end_number + 1)}
    }

    fa2.start_number += 1
    fa2.end_number += 1


"""Преобразование Regex в автомат Томпсона"""


def __thompson_regex_to_nfa(regex: Node, init_pos: int, finite_automata: FiniteAutomatonIndexed) -> FiniteAutomatonIndexed:
    if regex.value == "|":
        finite_automata.input_symbols.add(EPSILON)
        finite_automata.add_state(init_pos)
        alt_pos, finite_automata = __switching_to_fst_branch_if_alt(init_pos, finite_automata)
        fa1 = __thompson_regex_to_nfa(regex.children[1], finite_automata.start_number, finite_automata)

        end_copy = fa1.end_number

        fa1.start_number += 1
        fa1.end_number += 1

        fa1.transitions[alt_pos][EPSILON].add('q' + str(fa1.end_number))
        fa2 = __thompson_regex_to_nfa(regex.children[0], fa1.end_number, fa1)

        __add_alt_final_states(end_copy, fa2)

    elif regex.value == ".":
        finite_automata.input_symbols.add(EPSILON)
        fa1 = __thompson_regex_to_nfa(regex.children[1], finite_automata.end_number, finite_automata)
        fa1.final_states.add('q' + str(fa1.end_number))

        '''Добавление eps перехода между парсингом РВ'''
        fa1.transitions['q' + str(fa1.end_number)] = {
            EPSILON: {'q' + str(fa1.end_number + 1)}
        }

        fa1.start_number += 1
        fa1.end_number += 1

        fa2 = __thompson_regex_to_nfa(regex.children[0], fa1.end_number, fa1)

        fa2.final_states.add('q' + str(fa2.end_number))

    elif regex.value == "*":
        '''
        Начальное, конечное состояния перед eps переходом
        для eps перехода в последнее состояние
        '''
        start_copy = finite_automata.start_number
        finish_copy = finite_automata.end_number

        finite_automata.input_symbols.add(EPSILON)

        finite_automata.transitions['q' + str(finite_automata.start_number)] = {
            EPSILON: {'q' + str(finite_automata.end_number + 1)}
        }

        finite_automata.add_state(finite_automata.start_number)

        finite_automata.start_number += 1
        finite_automata.end_number += 1

        '''
        Начальное состояние перед парсингом регулярки
        для обратного eps перехода в это состояние
        '''
        s1_copy = finite_automata.start_number

        __thompson_regex_to_nfa(regex.children[0], finite_automata.end_number, finite_automata)

        finite_automata.transitions['q' + str(finite_automata.end_number)] = {
            EPSILON: {'q' + str(finite_automata.end_number + 1)}
        }

        '''Обратный eps переход'''
        finite_automata.transitions['q' + str(finite_automata.end_number)][EPSILON].add(
            'q' + str(s1_copy)
        )

        finite_automata.start_number += 1
        finite_automata.end_number += 1

        '''eps переход из начала в последнее состояние'''
        finite_automata.transitions['q' + str(start_copy)][EPSILON].add(
            'q' + str(finite_automata.end_number)
        )

        finite_automata.add_state(finite_automata.end_number)
        finite_automata.final_states.add('q' + str(finite_automata.end_number))

    elif regex.node_type.value == 3:

        finite_automata.add_state(init_pos)

        finite_automata.input_symbols.add(regex.value)

        finite_automata.transitions['q' + str(finite_automata.start_number)] = {
            regex.value: {'q' + str(finite_automata.end_number + 1)}
        }

        finite_automata.start_number += 1
        finite_automata.end_number += 1

        finite_automata.add_state(finite_automata.end_number)
        finite_automata.final_states.add('q' + str(finite_automata.start_number))

    return finite_automata


'''FiniteAutomatonIndexed to FiniteAutomaton'''


@registry.register(registry.FunctionType.REGULAR)
def Thompson(regex: Regex) -> FiniteAutomaton:
    init_pos = 0
    finite_automata = FiniteAutomatonIndexed(
        initial_state='q0',
        states=set(),
        transitions=dict(),
        final_states=set(),
        input_symbols=set(),
        start_number=0,
        source_regex=regex,
        end_number=0
    )

    __thompson_regex_to_nfa(regex.tree, init_pos, finite_automata)
    finite_automaton = FiniteAutomaton(
        finite_automata.initial_state,
        finite_automata.states,
        finite_automata.final_states,
        finite_automata.input_symbols,
        finite_automata.transitions,
        regex
    )
    return finite_automaton

