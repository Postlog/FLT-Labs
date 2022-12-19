import typing

from .fibonacci import fibonacci
from .test import test
import functions.registry as registry


def get_types(func: callable) -> tuple[list, list]:
    hints = typing.get_type_hints(func)

    input_types, output_types = [], []
    for key, value in hints.items():
        if key == 'return':
            if hasattr(value, '__args__'):
                output_types = list(value.__args__)
            else:
                output_types = [value]
            continue

        if hasattr(value, '__args__'):
            input_types.append(list(value.__args__))
        else:
            input_types.append(value)

    return input_types, output_types
