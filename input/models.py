import dataclasses
import typing

from models.base import Variable, Constant


@dataclasses.dataclass
class Action:
    pass


@dataclasses.dataclass
class AssignmentAction(Action):
    variable: Variable
    functions: list[callable]
    arguments: typing.List[typing.Union[Variable, Constant]]
    output_required: bool


@dataclasses.dataclass
class ExtraAction(Action):
    function: callable
    arguments: typing.List[typing.Union[Variable, Constant]]


@dataclasses.dataclass
class PredicateAction(Action):
    predicate: callable
    arguments: typing.List[typing.Union[Variable, Constant]]


__all__ = [
    'Action',
    'AssignmentAction',
    'ExtraAction',
    'PredicateAction',
]