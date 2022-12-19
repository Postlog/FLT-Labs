import dataclasses

from models.base import Type


@dataclasses.dataclass
class Bool(Type):
    """
    Тип, который может иметь значения True/False

    b = Bool(True)

    print(b.value) # 100
    """

    value: bool
