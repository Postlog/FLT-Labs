class Derivative:
    result = {
        "type": "",
        "first_arg": "",
        "second_arg": "",
    }

    def __init__(self, differential):
        self.differential = differential

    def get_type(self, regex, arg_index):
        if regex["type"] == "operation":
            self.check_operation(regex)
        elif regex["type"] == "symbol":
            if "second_arg" in regex:
                self.check_var(regex, arg_index)
            else:
                self.check_var(regex, arg_index)
        return self.result

    def check_operation(self, regex):
        self.result = {
            "type": "operation",
            "operation": "",
            "first_arg": "",
            "second_arg": ""
        }
        if regex["operation"] == "*":
            arg_index = 1
            self.result["operation"] = "concat"
            self.get_type(regex["first_arg"], arg_index)
            self.result["second_arg"] = regex
        elif regex["operation"] == "|":
            arg_index = 1
            self.get_type(regex["first_arg"], arg_index)
            self.result["operation"] = "|"
            arg_index = 2
            self.get_type(regex["second_arg"], arg_index)
        elif regex["operation"] == "concat":
            arg_index = 1
            self.get_type(regex["first_arg"], arg_index)
            # self.result["first_arg"] = regex["first_arg"]
            self.result["second_arg"] = regex["second_arg"]
            self.result["type"] = "|"
            self.derivative_concat(regex["first_arg"], regex["second_arg"])

    def check_var(self, var, arg_index):
        if len(var["value"]) == 1:
            self.derivative_var(var, arg_index)

    def derivative_var(self, var, arg_index):
        num_of_arg = ""
        if arg_index == 1:
            num_of_arg = "first_arg"
        elif arg_index == 2:
            num_of_arg = "second_arg"

        if var["value"] == self.differential:
            self.result[num_of_arg] = {}
            self.result[num_of_arg]["type"] = "symbol"
            self.result[num_of_arg]["value"] = ""
        elif var == "" or var != self.differential:
            self.result[num_of_arg] = {}
            self.result[num_of_arg]["type"] = "empty_set"

    def derivative_concat(self, first_arg, second_arg):
        if first_arg["type"] == "symbol" and first_arg["value"] == "":
            arg_index = 2
            self.get_type(second_arg, arg_index)
        else:
            del self.result["operation"]
            del self.result["type"]
            del self.result["second_arg"]

