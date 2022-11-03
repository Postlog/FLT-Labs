from itertools import combinations

from models.regex import Node, NodeType, Regex, RegexParser
from models.fa import FiniteAutomaton
from models.int import Int
from thompson import Thompson
from utils.derivative_utils import DerivativeBrzozovski, tree_to_regex
# import functions.registry as registry


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


# @registry.register(registry.FunctionType.REGULAR)
def PumpingLength(regex: str) -> int:
    regex_for_thompson = Regex(regex)
    nfa = Thompson(regex_for_thompson)
    # преобразование в дка (пока отсутствует)
    # dfa = minimize(nfa)
    parsed_regex = RegexParser.parse(regex)
    orig_tree = parsed_regex
    n = 0
    infix_left = ""
    pumped_flag = False
    pumping_prefixes = set()
    while n < 100:
        # строим префикс длины n
        # данный блок с накачкой префиксов готов
        prefixes = FiniteAutomaton.prefix(dfa, n)
        all_prefixes_pumped = True
        for prefix in prefixes:
            tree = orig_tree
            for symbol in prefix:
                # берем производную по префиксу
                derivative_brzozovski = DerivativeBrzozovski(symbol)
                derivative_reg_with_prefix = derivative_brzozovski.get_derivative(tree)
                derivative_reg_with_prefix_regex = tree_to_regex(derivative_reg_with_prefix)
                tree = derivative_reg_with_prefix
            comb = combinations(prefix, n)
            infixes_list = set([''.join(i) for i in comb])
            # перебираем все инфиксы по префиксу
            for infix in infixes_list:
                if infix != prefix:
                    infix_left = prefix.replace(infix, "", 1)
                if infix_left != prefix:
                    indexes = list(find_all(prefix, infix))
                    # накачиваем инфиксы
                    for index in indexes:
                        pumping_part = "(" + infix + ")" + "*"
                        pumping_regex = prefix
                        pumping_regex_inf = pumping_regex.replace(infix, "", 1)
                        pumping_regex = pumping_regex_inf[:index] + pumping_part + pumping_regex_inf[len(infix) + index:]
                        regex_to_check = pumping_regex + derivative_reg_with_prefix_regex
                        # оптимизируем перебор, проверяя, если наш префикс начинается с накачиваемого префикса
                        for pumping_prefix in pumping_prefixes:
                            if regex_to_check.startswith(pumping_prefix):
                                pumped_flag = True
                            else:
                                # проверка на пересечение накачимаевого слова и изначального регулярного выражения (пока отсутствует)
                                # pumped_flag = ksubset(regex_to_check, parsed_regex)
                        # добавляем накачиваемый префикс для дальнейшей оптимизации
                        if pumped_flag:
                            pumping_prefixes.add(prefix)
                        else:
                            all_prefixes_pumped = False
                if all_prefixes_pumped:
                    return n
                else:
                    n += 1
