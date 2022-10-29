from __future__ import annotations

import typing

from models.base import Type
from enum import Enum


class NodeType(Enum):
    CONCAT = 0
    ZERO_OR_MORE = 1
    ALT = 2
    SYMBOL = 3


class Node:
    def __init__(self, node_type: NodeType, value: str, children: list[Node]):
        self._node_type = node_type
        self._value = value
        self._children = children

    @property
    def node_type(self):
        return self._node_type

    @property
    def value(self):
        return self._value

    @property
    def children(self):
        return self._children

    def __repr__(self):
        value_repr = ''
        if self.node_type == NodeType.SYMBOL:
            value_repr = f'({self._value})'

        return f'{self.node_type.name}{value_repr}: [{", ".join(c.node_type.name for c in self.children)}]'

    __str__ = __repr__


class RegexSyntaxError(Exception):
    pass


class RegexParser:
    _precedence_map = {
        '(': 1,
        '|': 2,
        '.': 3,
        '*': 4,
    }

    @staticmethod
    def _get_precedence(c: str) -> int:
        return RegexParser._precedence_map.get(c, 5)

    @staticmethod
    def parse(raw_regex: str) -> Node:
        regex = RegexParser._add_concat_symbol(raw_regex)
        regex = RegexParser._to_prefix_notation(regex)
        last_nodes = []

        for char in regex:
            if RegexParser._is_alphabetic(char):
                last_nodes.append(Node(NodeType.SYMBOL, char, []))
            elif char in ('.', '|'):
                a, b = _pop(last_nodes), _pop(last_nodes)
                if a is None or b is None:
                    raise RegexSyntaxError('Некорректно заданное регулярное выражение')

                node_type = NodeType.CONCAT if char == '.' else NodeType.ALT

                last_nodes.append(Node(node_type, char, [a, b]))
            elif char == '*':
                a = _pop(last_nodes)
                if a is None:
                    raise RegexSyntaxError('Некорректно заданное регулярное выражение')

                last_nodes.append(Node(NodeType.ZERO_OR_MORE, char, [a]))

        if len(last_nodes) != 1:
            raise RegexSyntaxError('Некорректно заданное регулярное выражение')

        return last_nodes[0]

    @staticmethod
    def _to_prefix_notation(regex: str) -> str:
        output = []
        stack = []

        k = 0
        while k < len(regex):
            c = regex[k]
            if c == '(':
                stack.append(c)
            elif c == ')':
                while _peek(stack) is not None and _peek(stack) != '(':
                    output.append(stack.pop())

                if _pop(stack) is None:
                    raise RegexSyntaxError('Некорректно заданное регулярное выражение')
            else:
                while len(stack) > 0:
                    peeked_char = _peek(stack)

                    peeked_char_precedence = RegexParser._get_precedence(peeked_char)
                    current_char_precedence = RegexParser._get_precedence(c)

                    if peeked_char_precedence >= current_char_precedence:
                        if (val := _pop(stack)) is None:
                            raise RegexSyntaxError('Некорректно заданное регулярное выражение')
                        output.append(val)
                    else:
                        break
                stack.append(c)

            k += 1

        while len(stack) > 0:
            output.append(stack.pop())

        return "".join(output)

    @staticmethod
    def _is_alphabetic(c: str) -> bool:
        return c not in ('*', '|', '(', ')', '.')

    @staticmethod
    def _add_concat_symbol(regex: str) -> str:
        result = ""
        for current_char in regex:
            if len(result) > 0:
                prev_char = result[len(result) - 1]
                if (prev_char == ')' or RegexParser._is_alphabetic(prev_char) or prev_char == '*') and (
                        current_char == '(' or RegexParser._is_alphabetic(current_char)):
                    result += "."
            result += current_char
        return result


class Regex(Type):
    def __init__(self, tree: Node, source_str: str):
        self._tree = tree
        self._source_str = source_str

    @property
    def tree(self) -> Node:
        return self._tree

    @property
    def source_str(self):
        return self._source_str


def _peek(lst: list[typing.Any]) -> typing.Optional[typing.Any]:
    if len(lst) != 0:
        return lst[-1]
    return None


def _pop(lst: list[typing.Any]) -> typing.Optional[typing.Any]:
    if len(lst) != 0:
        return lst.pop()

    return None
