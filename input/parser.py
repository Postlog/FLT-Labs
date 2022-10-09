import typing

from models import Int, Regex, FunctionsChain, Function, Variable, Constant

from functions import functions, predicates, extras
from input.tokenizer import TokenStream, Tag
from input.models import Action, PredicateAction, ExtraAction, AssigmentAction
from input.exceptions import CustomSyntaxError, CustomSyntaxErrorWithLineNumber


class Parser:
    def __init__(self, stream: TokenStream):
        self._stream = stream
        self._actions: typing.List[Action] = []
        self._current_line_number = 1
        self._defined_variables_names = []

    def parse(self) -> typing.List[Action]:
        try:
            self._parse_expression()
        except CustomSyntaxError as error:
            raise CustomSyntaxErrorWithLineNumber(str(error), self._current_line_number)
        return self._actions

    def _parse_expression(self):
        while self._stream.has_next():
            self._parse_line()
            self._current_line_number += 1

    def _parse_line(self):
        token = self._stream.next()
        if token.tag == Tag.FUNCTION_NAME:
            if token.image in predicates:
                self._parse_predicate_line()
            elif token.image in extras:
                self._parse_extra_line()
            else:
                raise CustomSyntaxError(f'Неизвестная функция "{token.image}"')
        else:
            self._parse_assigment_line()

    def _parse_predicate_line(self):
        predicate = predicates[self._stream.last_fetched().image]

        token = self._stream.next()
        if token.tag in (Tag.EOS, Tag.LF):
            return

        arguments = self._parse_arguments()
        self._actions.append(PredicateAction(predicate, arguments))

    def _parse_extra_line(self):
        extra_function = extras[self._stream.last_fetched().image]

        arguments = []
        token = self._stream.next()
        if token.tag not in (Tag.EOS, Tag.LF):
            arguments = self._parse_arguments()

        self._actions.append(ExtraAction(extra_function, arguments))

    def _parse_assigment_line(self):
        token = self._stream.last_fetched()
        if token.tag != Tag.VARIABLE_NAME:
            raise CustomSyntaxError(f'Ожидалось имя переменной, но был встречен "{token.image}"')

        variable_name = token.image

        token = self._stream.next()
        if token.tag != Tag.EQUAL_SIGN:
            raise CustomSyntaxError(f'Ожидался знак равно, но был встречен "{token.image}"')

        token = self._stream.next()
        functions_list = []
        arguments = []
        output_required = False
        if token.tag == Tag.FUNCTION_NAME:
            functions_list = self._parse_functions()
            arguments = self._parse_arguments([Tag.DOUBLE_EXCLAMATION])

            token = self._stream.last_fetched()
            if token.tag == Tag.DOUBLE_EXCLAMATION:
                output_required = True
                token = self._stream.next()

            if token.tag not in (Tag.EOS, Tag.LF):
                raise CustomSyntaxError(f'Ожидался конец строки, но был встречен "{token.image}"')
        else:
            arguments.append(self._parse_argument())

            token = self._stream.next()
            if token.tag not in (Tag.EOS, Tag.LF):
                raise CustomSyntaxError(f'Ожидался конец строки, но был встречен "{token.image}"')

        self._defined_variables_names.append(variable_name)
        self._actions.append(AssigmentAction(
            Variable(variable_name),
            FunctionsChain(functions_list),
            arguments,
            output_required
        ))

    def _parse_arguments(self, tags_to_skip: typing.List[Tag] = None) -> typing.List[typing.Union[Variable, Constant]]:
        token = self._stream.last_fetched()
        arguments = []

        if tags_to_skip is None:
            tags_to_skip = []

        while token.tag not in (Tag.EOS, Tag.LF, *tags_to_skip):
            argument = self._parse_argument()
            arguments.append(argument)
            token = self._stream.next()

        return arguments

    def _parse_argument(self) -> typing.Union[Variable, Constant]:
        token = self._stream.last_fetched()

        if token.tag == Tag.REGEX:
            argument = Constant(Regex(token.image))
        elif token.tag == Tag.NUMBER:
            argument = Constant(Int(int(token.image)))
        elif token.tag == Tag.VARIABLE_NAME:
            if token.image not in self._defined_variables_names:
                raise CustomSyntaxError(f'Использование необъявленной переменной "{token.image}"')
            argument = Variable(token.image)
        else:
            raise CustomSyntaxError(f'Ожидался regex, число или имя переменной, но был встречен "{token.image}"')

        return argument

    def _parse_functions(self) -> typing.List[Function]:
        token = self._stream.last_fetched()
        if token.image not in functions:
            raise CustomSyntaxError(f'Неизвестная функция "{token.image}"')

        functions_list = [functions[token.image]]
        token = self._stream.next()

        while token.tag == Tag.DOT:
            token = self._stream.next()

            if token.tag != Tag.FUNCTION_NAME:
                raise CustomSyntaxError(f'Ожидалось название функции, но был встречен {token.image}')
            if token.image not in functions:
                raise CustomSyntaxError(f'Неизвестная функция "{token.image}"')

            functions_list.append(functions[token.image])

            token = self._stream.next()

        return functions_list


__all__ = [
    'Parser'
]
