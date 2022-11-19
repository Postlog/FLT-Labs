from models.regex import Node, NodeType
from derivative.utils import check_empty_value, clean_print, tree_to_regex


class DerivativeBrzozovskiException(Exception):
    pass

# Brzozovski derivative


def derivative_regex_brzozovski(symbol: str, tree: Node):
    res = tree
    if tree.node_type == NodeType.EMPTY_SET:
        res = Node(NodeType.EMPTY_SET, '4', [])
    elif tree.node_type == NodeType.SYMBOL:
        res = check_var(symbol, res)
    elif tree.node_type == NodeType.ZERO_OR_MORE:
        res = clean_print(Node(NodeType.CONCAT, '3', [derivative_regex_brzozovski(symbol, tree.children[0]), tree]))
    elif tree.node_type == NodeType.ALT:
        res = clean_print(Node(NodeType.ALT, '2', [derivative_regex_brzozovski(symbol, tree.children[0]),
                                                   derivative_regex_brzozovski(symbol, tree.children[1])]))
    elif tree.node_type == NodeType.CONCAT:
        left_tree = clean_print(
            Node(NodeType.CONCAT, '3', [derivative_regex_brzozovski(symbol, tree.children[0]), tree.children[1]]))
        if check_empty_value(tree.children[0]):
            right_tree = derivative_regex_brzozovski(symbol, tree.children[1])
        else:
            right_tree = Node(NodeType.EMPTY_SET, '4', [])
        res = clean_print(Node(NodeType.ALT, '2', [left_tree, right_tree]))
    else:
        raise DerivativeBrzozovskiException("Определена неверная операция")
    return res


def check_var(symbol: str, var: Node):
    if len(var.value) == 1:
        res = derivative_var(symbol, var)
    else:
        raise DerivativeBrzozovskiException("Неправильный пасринг регулярного выражения")
    return res


def derivative_var(symbol: str, var: Node):
    if var.value == symbol:
        res = Node(NodeType.SYMBOL, '', [])
    else:
        res = Node(NodeType.EMPTY_SET, '4', [])
    return res

# Antimirov derivative

def derivative_regex_antimirov(regex: Node, differential: str) -> set:
    if regex.node_type == NodeType.SYMBOL:
        antimirov_set = derivative_var_antimirov(regex.value, differential)
    elif regex.node_type == NodeType.ALT or regex.node_type == NodeType.CONCAT or regex.node_type == NodeType.ZERO_OR_MORE:
        if regex.node_type == NodeType.ALT:
            first_element_in_set = derivative_regex_antimirov(regex.children[0], differential)
            second_element_in_set = derivative_regex_antimirov(regex.children[1], differential)

            antimirov_set = set(list(first_element_in_set) + list(second_element_in_set))
        elif regex.node_type == NodeType.ZERO_OR_MORE:
            second_element_in_set = regex
            second_element_in_set_regex = tree_to_regex(second_element_in_set)
            first_elements_in_set = derivative_regex_antimirov(regex.children[0], differential)
            antimirov_set = set()
            for first_element_in_set in first_elements_in_set:
                antimirov_set.add(first_element_in_set + second_element_in_set_regex)
        elif regex.node_type == NodeType.CONCAT:
            second_element_in_first_element_in_set = regex.children[1]
            second_element_in_first_element_in_set_regex = tree_to_regex(second_element_in_first_element_in_set)
            first_elements_in_first_element_in_set = derivative_regex_antimirov(regex.children[0], differential)
            antimirov_set = set()
            for first_element_in_first_element_in_set in first_elements_in_first_element_in_set:
                antimirov_set.add(first_element_in_first_element_in_set
                                  + second_element_in_first_element_in_set_regex)

            if check_empty_value(regex.children[0]):
                second_elements_in_set = derivative_regex_antimirov(regex.children[1], differential)
                for second_element_in_set in second_elements_in_set:
                    antimirov_set.add(second_element_in_set)
        else:
            raise DerivativeBrzozovskiException("Определена неверная операция")
    elif regex.node_type == NodeType.EMPTY_SET:
        antimirov_set = set()
    else:
        raise DerivativeBrzozovskiException("Передано некорректное выражение")
    return antimirov_set


def derivative_var_antimirov(var: str, differential: str) -> set:
    if len(var) == 1:
        if var == differential:
            antimirov_set = {""}
        else:
            antimirov_set = set()
    else:
        raise DerivativeBrzozovskiException("Неправильный парсинг регулярного выражения")
    return antimirov_set
