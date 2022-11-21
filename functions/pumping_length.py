from itertools import combinations

from models.regex import Node, NodeType, Regex, RegexParser
from models.fa import FiniteAutomaton
from functions.thompson import Thompson
from derivative.derivatives import derivative_regex_brzozovski
from derivative.utils import tree_to_regex
from functions.subset import subset
from models.nfa import NFA

def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)


# @registry.register(registry.FunctionType.REGULAR)
def PumpingLength(regex: Regex) -> int:
    fa = Thompson(regex)
    nfa = NFA(
        initial_state=fa.initial_state,
        states=fa.states,
        final_states=fa.final_states,
        input_symbols=fa.input_symbols,
        transitions=fa.transitions
    )
    dfa = nfa.determinize()
    orig_tree = regex.tree
    n = 3
    infix_left = ""
    pumped_flag = False
    pumping_prefixes = set()
    # while n < 4:
    for n in range(3):
        n+=1
        # строим префикс длины n
        # данный блок с накачкой префиксов готов
        prefixes = FiniteAutomaton.prefix(dfa, n)
        prefixes = ['abb', 'aaa']

        all_prefixes_pumped = True
        for prefix in prefixes:
            tree = orig_tree
            print("prefix, n:", prefix, n)
            for symbol in prefix:
                derivative_brzozovski = tree
                # берем производную по префиксу
                derivative_brzozovski = derivative_regex_brzozovski(symbol, derivative_brzozovski)
                # derivative_reg_with_prefix = derivative_brzozovski.get_derivative(tree)
                derivative_reg_with_prefix_regex = tree_to_regex(derivative_brzozovski)
                print('der:', prefix, derivative_reg_with_prefix_regex)
                tree = derivative_brzozovski
            comb = combinations(prefix, n)
            infixes_list = set([''.join(i) for i in comb])
            print('infixes_list:', infixes_list)
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
                        str_to_check = pumping_regex + derivative_reg_with_prefix_regex
                        tree_to_check = RegexParser.parse(str_to_check)
                        regex_to_check = Regex(tree_to_check, str_to_check)
                        print('regex to check:', regex_to_check.source_str)
                        # оптимизируем перебор, проверяя, если наш префикс начинается с накачиваемого префикса
                        # for pumping_prefix in pumping_prefixes:
                        #     if regex_to_check.source_str.startswith(pumping_prefix):
                        #         pumped_flag = True
                        #         print(pumped_flag)
                        #     else:
                                # проверка на пересечение накачимаевого слова и изначального регулярного выражения (пока отсутствует)
                        pumped_flag = subset(regex_to_check, regex)
                        print('pumped flag:', pumped_flag)
                        # добавляем накачиваемый префикс для дальнейшей оптимизации
                        if pumped_flag:
                            pumping_prefixes.add(prefix)
                        else:
                            all_prefixes_pumped = False
                if all_prefixes_pumped:
                    print(n)
                    return n
                else:
                    n += 1
