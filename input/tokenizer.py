import enum
import dataclasses
import re
import typing

from functions import functions, predicates, extras


class Tag(enum.Enum):
    EOS = 0  # End of stream
    LF = 1  # New line
    VARIABLE_NAME = 2
    FUNCTION_NAME = 3
    NUMBER = 4
    REGEX = 6
    DOUBLE_EXCLAMATION = 5  # !!
    EQUAL_SIGN = 7
    DOT = 8


@dataclasses.dataclass
class Token:
    tag: Tag
    image: str

    def __str__(self) -> str:
        return f'Token(tag={self.tag.name} image="{self.image}")'


class TokenStream:
    def __init__(self, tokens: typing.List[Token]):
        self._tokens = tokens
        self._pointer = 0

    def next(self) -> Token:
        if not self.has_next():
            return Token(Tag.EOS, 'eos')

        token = self._tokens[self._pointer]
        self._pointer += 1

        return token

    def watch_next(self) -> Token:
        if not self.has_next():
            return Token(Tag.EOS, 'eos')

        return self._tokens[self._pointer]

    def last_fetched(self) -> Token:
        if self._pointer - 1 == -1:
            raise Exception('Указатель вышел за пределы')

        return self._tokens[self._pointer - 1]

    def has_next(self) -> bool:
        return self._pointer != len(self._tokens)


class Tokenizer:
    _defined_variables_names: typing.List[str] = []

    def tokenize(self, raw_input: str) -> TokenStream:
        lines = _sanitize_and_split(raw_input)
        self._defined_variables_names = _collect_variables_names(lines)

        tokens = []
        for line in lines:
            tokens.extend(self._tokenize_line(line))
            tokens.append(Token(Tag.LF, '\\n'))

        return TokenStream(tokens)

    def _tokenize_line(self, line: str) -> typing.List[Token]:
        tokens = []

        for symbol in line.split():
            if symbol == '=':
                tokens.append(Token(Tag.EQUAL_SIGN, symbol))
            elif symbol == '!!':
                tokens.append(Token(Tag.DOUBLE_EXCLAMATION, symbol))
            elif _is_function_name(symbol):
                tokens.append(Token(Tag.FUNCTION_NAME, symbol))
            elif self._is_variable_name(symbol):
                tokens.append(Token(Tag.VARIABLE_NAME, symbol))
            elif symbol.isnumeric():
                tokens.append(Token(Tag.NUMBER, symbol))
            elif '.' in symbol:  # '.' в символе => это вызов функций по цепочке
                for sub_symbol in re.split(r'(\W)', symbol):
                    if sub_symbol == '.':
                        tokens.append(Token(Tag.DOT, sub_symbol))
                    else:
                        tokens.append(Token(Tag.FUNCTION_NAME, sub_symbol))
            else:  # остается последний вариант - это регулярное выражение.
                tokens.append(Token(Tag.REGEX, symbol))

        return tokens

    def _is_variable_name(self, symbol: str) -> bool:
        return symbol in self._defined_variables_names


def _sanitize_and_split(raw_input: str) -> typing.List[str]:
    raw_input = raw_input.strip()
    raw_input = re.sub('\n+', '\n', raw_input)
    raw_input = re.sub(' +', ' ', raw_input)
    return [s.strip() for s in raw_input.splitlines()]


def _collect_variables_names(lines: typing.List[str]) -> typing.List[str]:
    variable_names = []
    for line in lines:
        symbol = line.split()[0]
        if not _is_function_name(symbol) and _is_valid_variable_name(symbol):
            variable_names.append(symbol)

    return variable_names


def _is_function_name(symbol: str) -> bool:
    return symbol in predicates or symbol in extras or symbol in functions


def _is_valid_variable_name(symbol: str) -> bool:
    return symbol != '!!' and symbol != '=' and not symbol.isnumeric()


__all__ = [
    'Tag',
    'Token',
    'TokenStream',
    'Tokenizer',
]
