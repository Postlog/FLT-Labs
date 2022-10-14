import copy

from models import Regex


class DerivativeBrzozowski:

    def __init__(self, differential: int) -> Regex:
        self.differential = differential

    def get_type(self, regex: Regex):
        if regex["type"] == "operation":
            self.check_operation(regex)
        elif regex["type"] == "symbol":
            self.check_var(regex)
        if regex == {}:
            regex["type"] = "empty_set"
        return regex

    def check_operation(self, regex: Regex):
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
            regex[first_arg] = self.get_type(regex[first_arg])
            if regex[first_arg]["type"] == symbol and regex[first_arg][value] == "":
                regex["type"] = operation
                regex[operation] = "*"
                regex[first_arg] = copied_regex[first_arg]
            elif regex[first_arg]["type"] == empty_set:
                regex["type"] = empty_set

        elif regex[operation] == "|":
            regex[first_arg] = self.get_type(regex[first_arg])
            regex[second_arg] = self.get_type(regex[second_arg])
            if regex[first_arg]["type"] == empty_set:
                self.delete_operation(second_arg, regex)
            elif regex[second_arg]["type"] == empty_set:
                self.delete_operation(first_arg, regex)

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
            regex[first_arg][first_arg] = self.get_type(copied_regex[first_arg])
            regex[first_arg][second_arg] = copied_regex_second_arg
            if regex[first_arg][first_arg]["type"] == empty_set:
                self.delete_key(second_arg, regex)
            if (copied_regex_first_arg["type"] == "symbol" and copied_regex_first_arg[value] == "") \
                    or (copied_regex["type"] == operation and copied_regex[operation] == "*"):
                regex[second_arg] = self.get_type(regex[second_arg])
                if regex[second_arg]["type"] == empty_set:
                    self.delete_key(first_arg, regex)
            else:
                regex[second_arg]["type"] = "empty_set"
                self.delete_key(first_arg, regex)
            if regex[first_arg]["type"] == symbol and regex[first_arg][value] == "":
                self.delete_operation(second_arg, regex)
                if first_arg in copied_regex_second_arg:
                    regex[first_arg] = copied_regex_second_arg[first_arg]

    def delete_operation(self, num_of_arg: str, regex: Regex):
        operation = "operation"
        value = "value"
        symbol = "symbol"
        copied_regex_dev_first_arg = copy.deepcopy(regex[num_of_arg])
        regex["type"] = copied_regex_dev_first_arg["type"]
        if regex["type"] == operation:
            regex[operation] = copied_regex_dev_first_arg[operation]
        elif regex["type"] == symbol:
            regex[value] = copied_regex_dev_first_arg[value]

    def delete_key(self, num_of_arg: str, regex: Regex):
        first_arg = "first_arg"
        second_arg = "second_arg"
        copied_regex_dev_first_arg = copy.deepcopy(regex[num_of_arg])
        self.delete_operation(num_of_arg, regex)
        regex[num_of_arg] = copied_regex_dev_first_arg[num_of_arg]
        if second_arg in copied_regex_dev_first_arg:
            regex[second_arg] = copied_regex_dev_first_arg[second_arg]
        if first_arg in copied_regex_dev_first_arg:
            regex[first_arg] = copied_regex_dev_first_arg[first_arg]

    def check_var(self, var: Regex):
        if len(var["value"]) == 1:
            self.derivative_var(var)

    def derivative_var(self, var: Regex):
        value = "value"
        if var[value] == self.differential:
            var[value] = ""
        elif var[value] != self.differential or var[value] == "":
            var["type"] = "empty_set"
            del var[value]


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
