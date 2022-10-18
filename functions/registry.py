import typing
from enum import Enum

__mapping = {}


class FunctionType(Enum):
    REGULAR = 0
    EXTRA = 1
    PREDICATE = 2


def register(func_type: FunctionType):
    def wrapper(func: callable):
        __mapping[func.__name__.lower()] = (func_type.value, func)

        return func

    return wrapper


def get_function(name: str) -> typing.Optional[callable]:
    _, func = __mapping.get(name.lower(), (None, None))

    return func


def has_function(name: str, function_type: FunctionType) -> bool:
    lower_name = name.lower()

    return lower_name in __mapping and __mapping[lower_name][0] == function_type.value
