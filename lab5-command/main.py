from semantics import PDASemantics as Semantics
from parser import PDAParser as Parser
import json
import sys
import re
from pprint import pprint
from pda import PDA


def get_grammar_and_test(i):
    with open(f'grammars_and_tests/{i}test.txt') as t:
        with open(f'grammars_and_tests/{i}grammar.g4') as g:
            return g.read(), t.read()


aa_regex = '''
    any_symbol\s*=\s*["']
    ([^;^'^"]+)
    ['"]\s*;
'''
ae_regex = '''
    eps_symbol\s*=\s*["']
    ([^;^'^"]+)
    ['"]\s*;
'''
sa_regex = '''
    stack_any\s*=\s*["']
    ([^;^'^"]+)
    ['"]\s*;
'''
se_regex = '''
    stack_eps\s*=\s*["']
    ([^;^'^"]+)
    ['"]\s*;
'''

if __name__ == '__main__':
    grammar_raw, test_raw = get_grammar_and_test(sys.argv[1])

    flags = dict()

    aa = re.search(aa_regex, grammar_raw, flags=re.X)
    flags['aa'] = aa.groups()[0] if aa else 'any_default'

    ae = re.search(ae_regex, grammar_raw, flags=re.X)
    flags['ae'] = ae.groups()[0] if ae else 'eps_default'

    sa = re.search(aa_regex, grammar_raw, flags=re.X)
    flags['sa'] = sa.groups()[0] if sa else 'stack_any_default'

    se = re.search(se_regex, grammar_raw, flags=re.X)
    flags['se'] = se.groups()[0] if se else 'stack_eps_default'

    print(grammar_raw)
    parser = Parser()
    semantics = Semantics()
    model, _ = parser.parse(test_raw, semantics=semantics)
    print(flags)
    print('##############')
    print(test_raw)
    print('##############')
    pprint(model)

    print('USER_DEFINED FLAGS:', flags)
    pda = PDA(model, flags)
    graph = pda.get_graphviz_notation()
    with open('graph.dot', 'w') as f:
        f.write(graph)
    # ast = generic_main(main, Parser, name='PDA', semantics=PDASemantics())
    # data = asjson(ast)
    # print(json.dumps(model, indent=2))
