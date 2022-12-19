import copy

from models.regex import Node, NodeType, Regex, RegexParser


def check_empty_value(regex: Node) -> bool:
    empty_value_flag = False
    if regex.node_type == NodeType.ALT or regex.node_type == NodeType.CONCAT or regex.node_type == NodeType.ZERO_OR_MORE:
        if regex.node_type == NodeType.ZERO_OR_MORE:
            empty_value_flag = True
        elif regex.node_type == NodeType.ALT:
            if regex.children[0].node_type == NodeType.SYMBOL and regex.children[0].value == "":
                empty_value_flag = True
            elif regex.children[1].node_type == NodeType.SYMBOL and regex.children[1].value == "":
                empty_value_flag = True
            else:
                return check_empty_value(regex.children[0]) or check_empty_value(regex.children[1])
    elif regex.node_type == NodeType.SYMBOL and regex.value == "":
        return True
    return empty_value_flag

class DerivativeBrzozovskiException(Exception):
    pass


class DerivativeBrzozovski:

    def __init__(self, differential: str):
        self.differential = differential

    def get_derivative(self, regex: Node) -> Node:
        regex_copy = copy.deepcopy(regex)
        return self.__get_derivative(regex_copy)

    def __get_derivative(self, regex: Node) -> Node:
        if regex.node_type == NodeType.SYMBOL:
            self.__check_var(regex)
        elif regex.node_type == NodeType.CONCAT or regex.node_type == NodeType.ALT\
                or regex.node_type == NodeType.ZERO_OR_MORE:
            self.__check_operation(regex)
        return regex

    def __check_operation(self, regex: Node) -> None:
        copied_regex = copy.deepcopy(regex)

        if regex.node_type == NodeType.ZERO_OR_MORE:
            regex.children.append(copied_regex)
            regex.node_type = NodeType.CONCAT
            regex.children[0] = self.__get_derivative(regex.children[0])

            if regex.children[0].node_type == NodeType.SYMBOL and regex.children[0].value == "":
                regex.node_type = NodeType.ZERO_OR_MORE
                regex.children[0] = copied_regex.children[0]
                del regex.children[1]
            elif regex.children[0].node_type == NodeType.EMPTY_SET:
                regex.node_type = NodeType.EMPTY_SET


        elif regex.node_type == NodeType.ALT:
            regex.children[0] = self.__get_derivative(regex.children[0])
            regex.children[1] = self.__get_derivative(regex.children[1])
            if regex.children[0].node_type == NodeType.EMPTY_SET:
                regex_second_arg = copied_regex.children[1]
                regex.node_type = regex_second_arg.node_type
                if regex_second_arg.node_type == NodeType.SYMBOL:
                    regex.value = regex_second_arg.value
                if regex_second_arg.node_type == NodeType.ALT or regex_second_arg.node_type == NodeType.ZERO_OR_MORE or regex_second_arg.node_type == NodeType.CONCAT:
                    regex.children[0] = regex_second_arg.children[0]
                    if len(regex.children[1].children) == 2:
                        regex.children[1] = regex_second_arg.children[1]
            if regex.children[1].node_type == NodeType.EMPTY_SET:
                regex_first_arg = copied_regex.children[0]
                regex.node_type = regex_first_arg.node_type
                if regex_first_arg.node_type == NodeType.SYMBOL:
                    regex.value = regex_first_arg.value
                if regex_first_arg.node_type == NodeType.ALT or regex_first_arg.node_type == NodeType.ZERO_OR_MORE or regex_first_arg.node_type == NodeType.CONCAT:
                    regex.children[0] = regex_first_arg.children[0]
                    if len(regex_first_arg.children) == 2:
                        regex.children[1] = regex_first_arg.children[1]

        elif regex.node_type == NodeType.CONCAT:
            empty_flag = check_empty_value(copied_regex.children[0])
            copied_regex_second_arg = copied_regex.children[1]
            regex.node_type = NodeType.ALT
            regex.children[0].node_type = NodeType.CONCAT
            first_element_in_first_element = self.__get_derivative(copied_regex.children[0])
            regex.children[0].children.append(first_element_in_first_element)
            regex.children[0].children.append(copied_regex_second_arg)
            if regex.children[0].children[0].node_type == NodeType.EMPTY_SET:
                regex.children[0].node_type = NodeType.EMPTY_SET

            elif regex.children[0].children[0].node_type == NodeType.SYMBOL and regex.children[0].children[0].value == "":
                regex.children[0].node_type = regex.children[1].node_type
                if copied_regex_second_arg.node_type == NodeType.SYMBOL:
                    regex.children[0].value = copied_regex_second_arg.value
                elif copied_regex_second_arg.node_type == NodeType.ALT or copied_regex_second_arg.node_type == NodeType.CONCAT or copied_regex_second_arg.node_type == NodeType.ZERO_OR_MORE:
                    regex.children[0].children[0] = copied_regex_second_arg.children[0]
                    if len(copied_regex_second_arg.children) == 2:
                        regex.children[0].children[1] = copied_regex_second_arg.children[1]
            if empty_flag:
                regex.children[1] = self.__get_derivative(regex.children[1])

            else:
                copied_regex_first_arg = copy.deepcopy(regex.children[0])
                regex.children[1].node_type = NodeType.EMPTY_SET
                regex.node_type = copied_regex_first_arg.node_type
                # print(tree_to_regex(regex))
                if copied_regex_first_arg.node_type == NodeType.SYMBOL:
                    regex.value = copied_regex_first_arg.value
                elif copied_regex_first_arg.node_type == NodeType.ALT or copied_regex_first_arg.node_type == NodeType.CONCAT or copied_regex_first_arg.node_type == NodeType.ZERO_OR_MORE:
                    regex.children[0] = copied_regex_first_arg.children[0]
                    if len(copied_regex_first_arg.children) == 2:
                        regex.children[1] = copied_regex_first_arg.children[1]

    def __check_var(self, var: Node) -> None:
        if len(var.value) == 1:
            self.__derivative_var(var)
        else:
            raise DerivativeBrzozovskiException("Неправильный пасринг регулярного выражения")

    def __derivative_var(self, var: Node) -> None:
        if var.value == self.differential:
            var.value = ""
        elif var.value != self.differential or var.value == "":
            var.node_type = NodeType.EMPTY_SET


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
        raise DerivativeBrzozovskiException("Неправильный пасринг регулярного выражения")
    return antimirov_set

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
