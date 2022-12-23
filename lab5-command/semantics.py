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
