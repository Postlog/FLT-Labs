from __future__ import annotations

import tatsu
from tatsu.buffering import Buffer
from tatsu.parsing import Parser
from tatsu.parsing import tatsumasu
from tatsu.parsing import leftrec, nomemo, isname
from tatsu.infos import ParserConfig
from tatsu.util import re, generic_main


def flatten(list_of_lists):
    if isinstance(list_of_lists, tatsu.contexts.closure):
        list_of_lists = list(list_of_lists)
    if len(list_of_lists) == 0:
        return []
    if isinstance(list_of_lists[0], list):
        return flatten(list_of_lists[0]) + flatten(list_of_lists[1:])
    return list_of_lists[:1] + flatten(list_of_lists[1:])


def lf(key, ast):
    return list(filter(lambda x: x[0] == key, ast))


def notlf(key, ast):
    return list(filter(lambda x: x[0] != key, ast))


class PDASemantics:
    def start(self, ast):
        return ast

    def stmts(self, ast):
        return ast

    def stmt(self, ast):
        statements = list(filter(lambda x: type(x) != str, ast))
        statements = notlf('statement_separator', statements)
        assert len(statements) == 1
        return statements[0][0]

    # отдельный узел
    def single_node_description(self, ast):
        ast = flatten(list(ast))
        elements = []
        for x in ast:
            if type(x) == tuple:
                elements.append(x)
            elif type(x) == str:
                pass
            else:
                raise Exception('что это')
        ids = lf('node_id', elements)
        assert len(ids) == 1
        lables = lf('node_label', elements)
        assert len(lables) <= 1
        initial_flag = lf('initial_flag', elements)
        final_flag = lf('final_flag', elements)
        trap_flag = lf('trap_flag', elements)
        transits = lf('single_node_transits', elements)
        ret = {
            'id': ids[0][1],
            'label': lables[0][1] if lables else None,
            'flags': [x[1] for x in lf('flag', elements)],
            'transits': [x[1] for x in transits[0][1]] if transits else []
        }
        return ('single_node_description', ret)

    def single_node_transits(self, ast):
        transits = lf('single_node_transit', flatten(ast))
        return ('single_node_transits', transits)

    def single_node_transit(self, ast):
        ast = list(ast)
        ast = flatten(ast)
        ids = lf('node_id', ast)
        assert len(ids) == 1
        flags = lf('transit_flag', ast)
        ret = {
            'dest_id': ids[0][1],
            'alphabeth_unit': lf('alphabeth_unit', ast)[0][1],
            'stack_pop_symbol': lf('stack_pop_symbol', ast)[0][1],
            'stack_push_symbols': [x[1] for x in lf('stack_push_symbol', ast)],
            'flags': [x[1] for x in flags]
        }
        return ('single_node_transit', ret)

    # отдельный переход
    def single_edge_description(self, ast):
        elements = []
        ast = flatten(list(ast))
        for x in ast:
            if type(x) == tuple:
                elements.append(x)
            elif type(x) == str:
                pass
            else:
                raise Exception('что это')
        ast = elements
        nodes_from = lf('node_from', ast)
        assert len(nodes_from) == 1
        nodes_to = lf('node_to', ast)
        assert len(nodes_to) == 1
        alphabeth_units = lf('alphabeth_unit', ast)
        assert len(alphabeth_units) == 1
        stack_pop_symbols = lf('stack_pop_symbol', ast)
        assert len(stack_pop_symbols) == 1
        stack_push_symbols = lf('stack_push_symbol', ast)
        assert len(stack_push_symbols) == 1
        flags = lf('transit_flag', ast)
        ret = {
            'node_from': nodes_from[0][1],
            'node_to': nodes_to[0][1],
            'alphabeth_unit': alphabeth_units[0][1],
            'stack_pop_symbol': stack_pop_symbols[0][1],
            'stack_push_symbols': [x[1] for x in stack_push_symbols],
            'flags': [x[1] for x in flags]
        }
        return ('single_transit_description', ret)

    # группа узлов
    def group_of_nodes(self, ast):
        elements = []
        ast = flatten(list(ast))
        for x in ast:
            if type(x) == tuple:
                elements.append(x)
            elif type(x) == str:
                pass
            else:
                raise Exception('что это')
        nodes = lf('node_id', elements)
        assert len(nodes) >= 1
        flags = lf('flag', elements)
        assert len(flags) >= 1
        ret = {
            'flags': [x[1] for x in flags],
            'nodes': [x[1] for x in nodes]
        }
        return ('group_of_nodes', ret)

    # метки узлов
    def node_ids(self, ast):
        return ('node_ids', [x[1] for x in ast])

    def node_id(self, ast):
        if ast[0] == 'string_literal':
            string_literals = [ast]
        else:
            string_literals = lf('string_literal', ast)
        assert len(string_literals) == 1
        return ('node_id', string_literals[0][1])

    def node_label(self, ast):
        if ast[0] == 'string_literal':
            string_literals = [ast]
        else:
            string_literals = lf('string_literal', ast)
        assert len(string_literals) == 1
        return ('node_label', string_literals[0][1])

    def node_from(self, ast):
        return ('node_from', ast[1])

    def node_to(self, ast):
        return ('node_to', ast[1])

    # для переходов
    def alphabeth_unit(self, ast):
        return ('alphabeth_units', ast)

    def alphabeth_unit(self, ast):
        return ('alphabeth_unit', ast)

    def alphabeth_symbol(self, ast):
        return ('alphabeth_symbol', ast)

    def eps_symbol(self, ast):
        return ('eps_symbol', ast)

    def any_symbol(self, ast):
        return ('any_symbol', ast)

    def stack_push_symbol(self, ast):
        return ('stack_push_symbol', ast)

    def stack_pop_symbol(self, ast):
        return ('stack_pop_symbol', ast)

    def stack_units(self, ast):
        return ('stack_units', ast)

    def stack_unit(self, ast):
        return ast

    def stack_symbol(self, ast):
        return ('stack_symbol', ''.join(flatten(list(ast))))

    def stack_any(self, ast):
        return ('stack_any',)

    def stack_eps(self, ast):
        return ('stack_eps',)

    # флаги
    def flag(self, ast):
        return ('flag', ast)

    def initial_flag(self, ast):
        return ('initial_flag',)

    def final_flag(self, ast):
        return ('final_flag',)

    def trap_flag(self, ast):
        return ('trap_flag',)

    def transit_flag(self, ast):
        return ('transit_flag', ast)

    def deterministic_flag(self, ast):
        return ('deterministic_flag',)

    def stack_independency_flag(self, ast):
        return ('stack_independency_flag',)

    # произвольные строковые литералы
    def string_literal_1(self, ast):
        return ('string_literal', ''.join(ast))

    def string_literal_2(self, ast):
        return ('string_literal', ''.join(ast))

    def string_literal_3(self, ast):
        return ('string_literal', ''.join(ast))

    def string_literal_4(self, ast):
        return ('string_literal', ''.join(ast))

    def string_literal_5(self, ast):
        return ('string_literal', ''.join(ast))

    def string_literal_6(self, ast):
        return ('string_literal', ''.join(ast))

    def string_literal_7(self, ast):
        return ('string_literal', ''.join(ast))

    # ключевые слова
    def key_word1(self, ast):
        return ('key_word',)

    def key_word2(self, ast):
        return ('key_word',)

    def key_word3(self, ast):
        return ('key_word',)

    def key_word4(self, ast):
        return ('key_word',)

    def key_word5(self, ast):
        return ('key_word',)

    def key_word6(self, ast):
        return ('key_word',)

    def key_word7(self, ast):
        return ('key_word',)
