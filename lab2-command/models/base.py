import dataclasses


class Type:
    """
    Базовый класс для всех типов
    """


@dataclasses.dataclass
class Variable:
    """
    Базовый класс для всех переменных
    """

    name: str


@dataclasses.dataclass
class Constant:
    """
    Базовый класс для всех констант
    """

    value: Type
