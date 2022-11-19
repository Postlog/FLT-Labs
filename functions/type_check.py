import typing
from input.models import Action, AssignmentAction, PredicateAction
from models.fa import FiniteAutomaton
from models.regex import Regex


GROUP1 = ['minimize', 'annote', 'de_annote', 'mergebisim', 'de_liniarize', 'linearize', 're_meps']
GROUP2 = ['complement', 'reverse']
GROUP3 = ['determinize']


def is_nfa_equal(nfa1: FiniteAutomaton, nfa2: FiniteAutomaton) -> bool:
    # кто-то (не я) должен был реализовать это:)
    raise NotImplementedError


def is_dfa_equal(dfa1: FiniteAutomaton, dfa2: FiniteAutomaton) -> bool:
    # кто-то (не я) должен был реализовать это:)
    raise NotImplementedError


def is_regex_equal(regex1: Regex, regex2: Regex) -> bool:
    # кто-то (не я) должен был реализовать это:)
    raise NotImplementedError


def remove_optional_functions(actions: [Action]) -> [Action]:
    for action_index, action in enumerate(actions):
        if isinstance(action, AssignmentAction):
            functions = action.functions
            functions.reverse()
            decision = [1 for _ in range(len(functions))]  # 0 - удалить # 1 - оставить

            for index, func in enumerate(functions):
                if index == 0:
                    continue
                curr_func = func
                prev_func = functions[index - 1]
                if curr_func.__name__ == prev_func.__name__ and curr_func.__name__ in GROUP1:
                    decision[index - 1] = 0

            new_functions1 = []
            for index, func in enumerate(functions):
                if decision[index]:
                    new_functions1.append(func)
                else:
                    print(f'removed function {func.__name__}')

            decision = [1 for _ in range(len(new_functions1))]
            for index, func in enumerate(new_functions1):
                if index == 0:
                    continue
                curr_func = func
                prev_func = new_functions1[index - 1]
                if curr_func.__name__ in GROUP2 and prev_func.__name__ == curr_func.__name__:
                    decision[index] = 0
                    decision[index - 1] = 0

            new_functions2 = []
            for index, func in enumerate(new_functions1):
                if decision[index]:
                    new_functions2.append(func)
                else:
                    print(f'removed function {func.__name__}')

            decision = [1 for _ in range(len(new_functions2))]
            for index, func in enumerate(new_functions2):
                if index == 0:
                    continue
                curr_func = func
                prev_func = new_functions2[index - 1]
                if curr_func.__name__ in GROUP3 and prev_func.__name__ == 'thompson':
                    decision[index] = 0

            new_functions3 = []
            for index, func in enumerate(new_functions2):
                if decision[index]:
                    new_functions3.append(func)
                else:
                    print(f'removed function {func.__name__}')

            new_functions3.reverse()
            actions[action_index] = new_functions3


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

    if len(args) != len(input_types):
        raise TypeError(f'Invalid number of input arguments in function {func.__name__}')

    for i, arg in enumerate(args):
        if type(input_types[i]) == list:  # случай, когда input_types[i] - список возможных типов
            flag = False
            for variable_type in input_types[i]:
                if isinstance(arg, variable_type):
                    flag = True
            if not flag:
                raise TypeError(
                    f'Types incorrect: expected type = {input_types[i]}, got = {type(arg)}'
                )
        elif not isinstance(arg, input_types[i]):
            raise TypeError(f'Types incorrect: expected type = {input_types[i]}, got = {type(arg)}')
    else:
        # проверка того, поменяла ли операция входные данные или нет
        if output_types[0] == type(FiniteAutomaton):
            result = func(*args)
            if result.is_deterministic() and is_dfa_equal(result, *args):
                print(f'functional {func.__name__} is optional')
            elif not result.is_deterministic() and (is_nfa_equal(result, *args)):
                print(f'functional {func.__name__} is optional')
        elif output_types[0] == type(Regex):
            result = func(*args)
            if is_regex_equal(result, *args):
                print(f'functional {func.__name__} is optional')


def static_check(actions: [Action]) -> None:
    # final_actions = deepcopy(actions)
    variables = {}
    # тут должен быть алгоритм, который убирает лишние функции
    remove_optional_functions(actions)

    for action_index, action in enumerate(actions):  # итерируемся по действиям

        if isinstance(action, AssignmentAction):
            # функции выполняются с конца списка в начало (справа налево)
            functions = action.functions.reverse()
            input_arguments = action.arguments
            for i, function in enumerate(functions):  # итерируемся по функциям в action'e
                input_types, output_types = get_types(function)
                if len(input_arguments) != len(
                    input_types
                ):  # неправильное количество входных аргументов
                    raise TypeError(
                        f'Invalid number of input arguments in function {function.__name__}'
                    )
                if i == 0:  # случай первой функции в action'e
                    for j, arg in enumerate(input_arguments):
                        # проверяем совместимость входных аргументов с теми аргументами, которые должны подаваться на вход функции
                        if type(
                            input_types[j]
                        ) == list:  # случай, когда input_types[j] - список возможных типов
                            flag = False
                            for variable_type in input_types[j]:
                                if variables[arg] == variable_type:
                                    flag = True
                                    break
                            if not flag:
                                raise TypeError(
                                    f'Types incorrect: expected type = {input_types[j]}, got = {type(arg)}'
                                )
                        elif variables[arg] != input_types[j]:
                            raise TypeError(
                                f'Types incorrect: expected type = {input_types[j]}, got = {type(arg)}'
                            )
                else:  # случай для 2 и последующих функций в action'e
                    for j, arg in enumerate(input_arguments):
                        if type(input_types[j]) == list:
                            flag = False
                            for variable_type in input_types[j]:
                                if arg == variable_type:
                                    flag = True
                                    break
                            if not flag:
                                raise TypeError(
                                    f'Types incorrect: expected type = {input_types[j]}, got = {arg}'
                                )
                        elif arg != input_types[j]:
                            raise TypeError(
                                f'Types incorrect: expected type = {input_types[j]}, got = {type(arg)}'
                            )
                input_arguments = output_types
            variables[action.variable] = output_types

        else:
            if isinstance(action, PredicateAction):
                function = action.predicate
            else:
                function = action.function

            input_arguments = action.arguments
            input_types, output_types = get_types(function)

            if len(input_arguments) != len(input_types):  # проверка длины
                raise TypeError(
                    f'Invalid number of input arguments in function {function.__name__}'
                )

            for i, arg in enumerate(input_arguments):  # проверка входных типов
                if type(input_types[i]) == list:
                    flag = False
                    for variable_type in input_types[i]:
                        if arg == variable_type:
                            flag = True
                            break
                    if not flag:
                        raise TypeError(
                            f'Types incorrect: expected type = {input_types[i]}, got = {arg}'
                        )
                elif not isinstance(arg, input_types[i]):
                    raise TypeError(
                        f'Types incorrect: expected type = {input_types[i]}, got = {type(arg)}'
                    )
