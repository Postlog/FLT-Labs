import dataclasses
import typing

from models.base import Variable, Constant
from models.function import FunctionsChain, Function


@dataclasses.dataclass
class Action:
    pass


@dataclasses.dataclass
class AssigmentAction(Action):
    variable: Variable
    functions: FunctionsChain
    arguments: typing.List[typing.Union[Variable, Constant]]
    output_required: bool


@dataclasses.dataclass
class ExtraAction(Action):
    function: Function


@dataclasses.dataclass
class PredicateAction(Action):
    predicate: Function
    arguments: typing.List[typing.Union[Variable, Constant]]
