import typing
import string

from models.base import Type
from enum import Enum


class Operation(Enum):
    OR = "|"
    ZERO_OR_ONE = "?"
    ONE_OR_MORE = "+"
    ZERO_OR_MORE = "*"
    GROUP_START = "("
    GROUP_END = ")"

    @staticmethod
    def get_symbols() -> typing.List[str]:
        return [o.value for o in Operation]


class RegexSyntaxError(Exception):
    pass


class Regex(Type):
    _tree: typing.Any

    def __init__(self, regex: str):
        self._tree = Regex._parse(regex)

    @property
    def tree(self) -> typing.List[typing.Any]:
        return self.tree

    @staticmethod
    def _parse(regex: str) -> typing.Any:
        symbols = Operation.get_symbols()
        for i, c in enumerate(regex):
            if not (c in symbols or c in string.ascii_letters or c in string.digits):
                raise RegexSyntaxError(
                    f'Регулярное выражение "{regex}" содержит недопустимый символ "{c}" на позиции {i}'
                )

        # TODO: реализовать

        return []
