import typing
import argparse

from input.tokenizer import Tokenizer
from input.parser import Parser
from input.reader import read
from input.exceptions import CustomSyntaxErrorWithLineNumber
from input.models import AssignmentAction, ExtraAction, PredicateAction
from models import Variable, Constant
from logger import logger


def parse_flags() -> bool:
    parser = argparse.ArgumentParser(description='Реализация 2 лабораторной работы по ТФЯ')
    parser.add_argument(
        '--dynamic',
        action='store_true',
        dest='use_dynamic_type_checker',
        default=False,
        help='Использовать динамическую проверку типов вместо статической (тайпчекеры пока не реализованы)',
    )

    return parser.parse_args().use_dynamic_type_checker


def execute():
    use_dynamic_type_check = parse_flags()

    raw_input = read()
    t = Tokenizer()
    stream = t.tokenize(raw_input)

    p = Parser(stream)

    try:
        actions = p.parse()
    except CustomSyntaxErrorWithLineNumber as e:
        logger.warning(f'Ошибка синтаксиса: {e}')
        return

    if not use_dynamic_type_check:
        logger.info('static check used')
        # actions = static_check(actions)
    else:
        logger.info('dynamic check used')

    values = dict()
    for action in actions:
        if isinstance(action, AssignmentAction):
            values[action.variable.name] = __call_functions_chain(
                action.functions,
                __get_arguments(action.arguments, values),
                use_dynamic_type_check,
            )
        elif isinstance(action, ExtraAction):
            action.function(*__get_arguments(action.arguments, values))
        elif isinstance(action, PredicateAction):
            action.predicate(*__get_arguments(action.arguments, values))
        else:
            raise Exception(f'Неожиданный тип action: {type(action)}')


def __get_arguments(args: typing.List[typing.Union[Variable, Constant]], values: dict) -> typing.List[typing.Any]:
    result = []
    for arg in args:
        if isinstance(arg, Variable):
            result.append(*values[arg.name])
        elif isinstance(arg, Constant):
            result.append(arg.value)
        else:
            raise Exception(f'Неожиданный тип аргумента: {type(arg)}')

    return result


def __call_functions_chain(funcs: list[callable], args: list[typing.Any], with_type_check: bool) -> list[typing.Any]:
    for func in funcs:
        if with_type_check:
            logger.debug(f'dynamic checking of func {func.__name__}')
            # changed = dynamic_check(func, args)
            pass
        args = func(*args)
    return args
