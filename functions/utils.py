import copy

from models import Regex, Function


class DerivativeBrzozovski(Function):

    def __init__(self, differential: str):
        self.differential = differential

    def get_derivative(self, regex: str) -> Regex:
        if regex["type"] == "operation":
            self.check_operation(regex)
        elif regex["type"] == "symbol":
            self.check_var(regex)
        if regex == {}:
            regex["type"] = "empty_set"
        return regex

    def check_operation(self, regex: Regex) -> None:
        first_arg = "first_arg"
        second_arg = "second_arg"
        operation = "operation"
        concat = "concat"
        value = "value"
        empty_set = "empty_set"
        symbol = "symbol"

        if regex[operation] == "*":
            copied_regex = copy.deepcopy(regex)
            regex[second_arg] = copied_regex
            regex[operation] = concat
            regex[first_arg] = self.get_derivative(regex[first_arg])
            if regex[first_arg]["type"] == symbol and regex[first_arg][value] == "":
                regex["type"] = operation
                regex[operation] = "*"
                # self.delete_operation(second_arg, regex)
                regex[first_arg] = copied_regex[first_arg]
                del regex[second_arg]
            elif regex[first_arg]["type"] == empty_set:
                regex["type"] = empty_set

        elif regex[operation] == "|":
            regex[first_arg] = self.get_derivative(regex[first_arg])
            regex[second_arg] = self.get_derivative(regex[second_arg])
            if regex[first_arg]["type"] == empty_set:
                self.delete_operation(second_arg, regex)
                if regex[second_arg]["type"] == operation:
                    regex[first_arg] = regex[second_arg][first_arg]
                if second_arg in regex[second_arg]:
                    regex[second_arg] = regex[second_arg][second_arg]
                del regex[second_arg]
            elif regex[second_arg]["type"] == empty_set:
                self.delete_operation(first_arg, regex)
                regex[second_arg] = regex[first_arg]
                # if second_arg in regex[first_arg]:
                #     regex[]
                del regex[first_arg]

        elif regex[operation] == concat:
            copied_regex = copy.deepcopy(regex)
            copied_regex_second_arg = copy.deepcopy(regex[second_arg])
            copied_regex_first_arg = copy.deepcopy(regex[first_arg])
            regex[operation] = "|"
            regex[first_arg] = {
                "type": "",
                operation: "",
                first_arg: {},
                second_arg: {},
            }
            regex[first_arg]["type"] = operation
            regex[first_arg][operation] = concat
            regex[first_arg][first_arg] = self.get_derivative(copied_regex[first_arg])
            regex[first_arg][second_arg] = copied_regex_second_arg
            if regex[first_arg][first_arg]["type"] == empty_set:
                self.delete_key(second_arg, regex)
            if check_empty_value(regex[first_arg]):
                regex[second_arg] = self.get_derivative(regex[second_arg])
                if regex[second_arg]["type"] == empty_set:
                    self.delete_key(first_arg, regex)
            else:
                regex[second_arg]["type"] = "empty_set"
                self.delete_key(first_arg, regex)
            if regex[first_arg]["type"] == symbol and regex[first_arg][value] == "":
                self.delete_operation(second_arg, regex)
                if first_arg in copied_regex_second_arg:
                    regex[first_arg] = copied_regex_second_arg[first_arg]

    def delete_operation(self, num_of_arg: str, regex: Regex) -> None:
        operation = "operation"
        value = "value"
        symbol = "symbol"
        copied_regex_dev_first_arg = copy.deepcopy(regex[num_of_arg])
        regex["type"] = copied_regex_dev_first_arg["type"]
        if regex["type"] == operation:
            regex[operation] = copied_regex_dev_first_arg[operation]
        elif regex["type"] == symbol:
            regex[value] = copied_regex_dev_first_arg[value]

    def delete_key(self, num_of_arg: str, regex: Regex) -> None:
        first_arg = "first_arg"
        second_arg = "second_arg"
        copied_regex_dev_first_arg = copy.deepcopy(regex[num_of_arg])
        self.delete_operation(num_of_arg, regex)
        regex[num_of_arg] = copied_regex_dev_first_arg[num_of_arg]
        if second_arg in copied_regex_dev_first_arg:
            regex[second_arg] = copied_regex_dev_first_arg[second_arg]
        if first_arg in copied_regex_dev_first_arg:
            regex[first_arg] = copied_regex_dev_first_arg[first_arg]

    def check_var(self, var: Regex) -> None:
        if len(var["value"]) == 1:
            self.derivative_var(var)
        else:
            print("Wrong parse")

    def derivative_var(self, var: Regex) -> None:
        value = "value"
        if var[value] == self.differential:
            var[value] = ""
        elif var[value] != self.differential or var[value] == "":
            var["type"] = "empty_set"
            del var[value]


def check_empty_value(regex: Regex) -> bool:
    first_arg = "first_arg"
    second_arg = "second_arg"
    operation = "operation"
    value = "value"
    symbol = "symbol"
    empty_value_flag = False

    if regex["type"] == operation:
        if regex[operation] == "*":
            empty_value_flag = True
        elif regex[operation] == "|":
            if regex[first_arg]["type"] == symbol and regex[first_arg][value] == "":
                empty_value_flag = True
            elif regex[second_arg]["type"] == symbol and regex[second_arg][value] == "":
                empty_value_flag = True
            else:
                return check_empty_value(regex[first_arg]) or check_empty_value(regex[second_arg])
    elif regex["type"] == symbol and regex[value] == "":
        return True
    return empty_value_flag


class DerivativeAntimirov(Function):
    def derivative_regex(self, regex: Regex, differential: str) -> set:
        first_arg = "first_arg"
        second_arg = "second_arg"
        operation = "operation"
        concat = "concat"
        value = "value"
        empty_set = "empty_set"
        symbol = "symbol"

        if regex["type"] == symbol:
            antimirov_set = self.derivative_var(regex[value], differential)
        elif regex["type"] == operation:
            if regex[operation] == "|":
                first_element_in_set = self.derivative_regex(regex[first_arg], differential)
                second_element_in_set = self.derivative_regex(regex[second_arg], differential)

                antimirov_set = set(list(first_element_in_set) + list(second_element_in_set))
            elif regex[operation] == "*":
                second_element_in_set = regex
                second_element_in_set_regex = tree_to_regex(second_element_in_set)
                first_elements_in_set = self.derivative_regex(regex[first_arg], differential)
                antimirov_set = set()
                for first_element_in_set in first_elements_in_set:
                    antimirov_set.add(first_element_in_set + second_element_in_set_regex)
            elif regex[operation] == concat:
                second_element_in_first_element_in_set = regex[second_arg]
                second_element_in_first_element_in_set_regex = tree_to_regex(second_element_in_first_element_in_set)
                first_elements_in_first_element_in_set = self.derivative_regex(regex[first_arg], differential)
                antimirov_set = set()
                for first_element_in_first_element_in_set in first_elements_in_first_element_in_set:
                    antimirov_set.add(first_element_in_first_element_in_set
                                      + second_element_in_first_element_in_set_regex)

                if check_empty_value(regex[first_arg]):
                    second_element_in_set = self.derivative_regex(regex[second_arg], differential)
                    antimirov_set.add(second_element_in_set)
            else:
                print("Wrong operation")
        elif regex["type"] == empty_set:
            antimirov_set = set()
        return antimirov_set

    def derivative_var(self, var: str, differential: str) -> set:
        if len(var) == 1:
            if var == differential:
                antimirov_set = {""}
            else:
                antimirov_set = set()
        else:
            print("Wrong parse")
        return antimirov_set

def tree_to_regex(tree: Regex) -> str:
    if tree['type'] == 'empty_set':
        return "_EMPTYSET_"
    elif tree['type'] == 'symbol':
        if tree['value'] == '':
            return '_EPSILON_'
        return tree['value']
    elif tree['type'] == 'operation':
        if tree['operation'] == "concat":
            return tree_to_regex(tree['first_arg']) + tree_to_regex(tree['second_arg'])
        elif tree['operation'] == "*":
            return f"({tree_to_regex(tree['first_arg'])})*"
        elif tree['operation'] == "|":
            return f"({tree_to_regex(tree['first_arg'])}|{tree_to_regex(tree['second_arg'])})"
