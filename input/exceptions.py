class CustomSyntaxError(Exception):
    pass


class CustomSyntaxErrorWithLineNumber(CustomSyntaxError):
    def __init__(self, message: str, line_number: int):
        super().__init__(message)
        self._line_number = line_number

    def __str__(self):
        return super().__str__() + f'. Номер строки: {self._line_number}'


class DerivativeBrzozovskiExceptions(Exception):
    pass


__all__ = [
    'CustomSyntaxError',
    'CustomSyntaxErrorWithLineNumber'
]