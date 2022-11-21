from models.regex import Node, NodeType

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


def clean_print(tree: Node):
    if tree.node_type == NodeType.CONCAT:
        if tree.children[0].node_type == NodeType.EMPTY_SET or tree.children[1].node_type == NodeType.EMPTY_SET:
            return Node(NodeType.EMPTY_SET, '4', [])
        elif tree.children[0].node_type == NodeType.SYMBOL and tree.children[0].value == '':
            return tree.children[1]
        elif tree.children[1].node_type == NodeType.SYMBOL and tree.children[1].value == '':
            return tree.children[0]
    elif tree.node_type == NodeType.ZERO_OR_MORE:
        if tree.children[0].node_type == NodeType.EMPTY_SET:
            return Node(NodeType.EMPTY_SET, '4', [])
        elif tree.children[0].node_type == NodeType.SYMBOL and tree.children[0].value == '':
            return Node(NodeType.SYMBOL, '', [])
    elif tree.node_type == NodeType.ALT:
        if tree.children[0].node_type == NodeType.EMPTY_SET:
            return tree.children[1]
        elif tree.children[1].node_type == NodeType.EMPTY_SET:
            return tree.children[0]
    return tree


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
