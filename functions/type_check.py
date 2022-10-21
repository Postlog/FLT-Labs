import typing


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


def dynamic_check(func: callable, *args, **kwargs) -> None:
    input_types, output_types = get_types(func)
    for i, arg in enumerate(args):
        if not isinstance(arg, input_types[i]):
            raise TypeError(f'Types incorrect: expected type = {input_types[i]}, got = {type(arg)}')
    else:
        if input_types == output_types:
            print(f'function {func} is optional!')
        print(f'Types correct')


def static_check(funcs: list[callable], *args) -> None:
    input_types = args
    for func in funcs:
        target_input_types, target_output_types = get_types(func)
        for i, expected_type in enumerate(target_input_types):
            if not isinstance(input_types[i], expected_type):
                raise TypeError(
                    f'Types incorrect in function {func}: expected type = {expected_type}, got = {type(input_types[i])}'
                )
        input_types = target_output_types
    else:
        print('Types correct!')
