from semantics import PDASemantics as Semantics
from parser import PDAParser as Parser
import json
import sys
from pprint import pprint
from pda import PDA

def get_grammar_and_test(i):
    with open(f'grammars_and_tests/{i}test.txt') as t:
        with open(f'grammars_and_tests/{i}grammar.g4') as g:
            return g.read(), t.read()


if __name__ == '__main__':
    grammar_raw, test_raw = get_grammar_and_test(sys.argv[1])
    print(grammar_raw)
    parser = Parser()
    semantics = Semantics()
    model = parser.parse(test_raw, semantics=semantics)
    print('##############')
    print(test_raw)
    print('##############')
    pprint(model)
    
    pda = PDA(model)
    graph = pda.get_graphviz_notation()
    with open('graph.dot', 'w') as f:
        f.write(graph)
    # ast = generic_main(main, Parser, name='PDA', semantics=PDASemantics())
    # data = asjson(ast)
    # print(json.dumps(model, indent=2))
