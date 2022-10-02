import dataclasses

from models.base import Type


@dataclasses.dataclass
class Int(Type):
    """
    Тип, который может принимать значения целого числа

    i = Int(100)

    print(i.value) # 100
    """

    value: int
