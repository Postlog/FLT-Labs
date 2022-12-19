import dataclasses
import typing

from models.base import Type


@dataclasses.dataclass
class NullableBool(Type):
    """
    Тип, который может иметь значения True/False/None

    ub = NullableBool(None)

    print(b.value) # None

    ub = NullableBool(True)

    print(b.value) # True
    """

    value: typing.Optional[bool]
