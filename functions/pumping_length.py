from itertools import combinations

from models.regex import Node, NodeType, Regex, RegexParser
from utils.derivative_utils import DerivativeBrzozovski

class PumpLength:
    def count_pump_length(self, regex):
        for i in range(len(regex)):
            # строим префикс
            prefix = self.make_prefix(regex, i)
            for symbol in prefix:
                # берем производную по префиксу
                derivative_brzozovski = DerivativeBrzozovski(symbol)
                derivative_reg_with_prefix = derivative_brzozovski.get_derivative(regex)
                derivative_reg_with_prefix_regex = tree_to_regex(derivative_reg_with_prefix)
            # перебираем все инфиксы
            infixes = combinations(prefix, i)
            infixes_list = ([''.join(i) for i in infixes])
            for infix in infixes_list:
                if infix != prefix:
                    infix_left = prefix.replace(infix, "", 1)
                if infix_left != prefix:
                    index = prefix.index(infix)
                    pumping_part = "(" + infix + ")" + "*"
                    pumping_regex = prefix
                    pumping_regex_inf = pumping_regex.replace(infix, "", 1)
                    pumping_regex = pumping_regex_inf[:index] + pumping_part + pumping_regex_inf[index:]
                    regex_to_check = pumping_regex + derivative_reg_with_prefix_regex
                    # проверяем входят ли они в наш язык
                    sub_set_flag = ksubset(regex_to_check, regex)
                    if sub_set_flag == True:
                        return i


def tree_to_regex(tree: Node) -> str:
    if tree.node_type == NodeType.EMPTY_SET:
        return "_EMPTYSET_"
    elif tree.node_type == NodeType.SYMBOL:
        if tree.value == '':
            return '_EPSILON_'
        return tree.value
    else:
        if tree.node_type == NodeType.CONCAT:
            return tree_to_regex(tree.children[0]) + tree_to_regex(tree.children[1])
        elif tree.node_type == NodeType.ZERO_OR_MORE:
            return f"({tree_to_regex(tree.children[0])})*"
        elif tree.node_type == NodeType.ALT:
            return f"({tree_to_regex(tree.children[0])}|{tree_to_regex(tree.children[1])})"