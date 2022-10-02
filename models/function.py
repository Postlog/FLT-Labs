from __future__ import annotations

import abc
import typing

from models.base import Type


class FunctionStep(abc.ABC):
    """
    Базовый класс для описания шагов выполнения функции
    """

    @abc.abstractmethod
    def __str__(self):
        pass


class Function(abc.ABC):
    """
    Абстрактный класс для всех функций.
    Имеет свойства:
     * input_types (типы, которые должны быть переданы в функцию)
     * output_types (типы, которые должны быть возвращены из функции)
    """

    _steps: typing.List[FunctionStep] = []

    def call(self, *args):
        self._steps = []
        return self._call_function(*args)

    @abc.abstractmethod
    def _call_function(self, *args):
        pass

    @property
    def steps(self) -> typing.List[FunctionStep]:
        return self._steps

    @property
    def input_types(
            self
    ) -> typing.List[typing.Union[typing.Type[Type], typing.List[typing.Type[Type]]]]:
        hints = typing.get_type_hints(self._call_function)

        types = []
        for key, value in hints.items():
            if key == 'return':
                continue

            if hasattr(value, '__args__'):
                types.append(list(value.__args__))
            else:
                types.append(value)

        return types

    @property
    def output_types(self) -> typing.List[typing.Type[Type]]:
        hints = typing.get_type_hints(self._call_function)
        return_hint = hints['return']

        if hasattr(return_hint, '__args__'):
            return list(return_hint.__args__)

        return [return_hint]


class FunctionsChain:
    """
    Класс, содержащий в себе функции, которые должны быть вызваны по цепочке
    """

    _steps: typing.List[typing.List[FunctionStep]] = []

    def __init__(self, functions: typing.List[Function]):
        self._functions = functions

    def execute(self, *args) -> typing.Any:
        self._steps = []

        result: typing.Any = args
        for i in range(len(self._functions) - 1, -1, -1):
            func = self._functions[i]
            result = func.call(*result)

            self._steps.append(func.steps)

        return result

    def get_functions(self) -> typing.List[Function]:
        return self._functions

    def remove_function(self, function: Function) -> None:
        self._functions.remove(function)

    @property
    def steps(self) -> typing.List[typing.List[FunctionStep]]:
        return self._steps
