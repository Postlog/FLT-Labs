import networkx as nx
from copy import deepcopy

ALA = 'any_symbol'
ALE = 'eps_symbol'
STA = 'stack_any'
STE = 'stack_eps'


class Transit:
    def __init__(self, node_from, node_to, alphabeth_unit, stack_pop_symbol, stack_push_symbols, flags):
        self.node_from = node_from
        self.node_to = node_to
        self.type = alphabeth_unit[0]
        self.alphabeth_symbol = alphabeth_unit[1] if alphabeth_unit[0] == 'alphabeth_symbol' else alphabeth_unit[0]
        self.stack_pop_symbol = stack_pop_symbol[1] if len(
            stack_pop_symbol) == 2 else stack_pop_symbol[0]
        stack_push_symbols = list(
            map(lambda x: x[1] if len(x) == 2 else x[0], stack_push_symbols))
        # если только eps, то весь = [eps], иначе почистим на лишние eps
        if any(map(lambda x: x == STE, stack_push_symbols)):
            stack_push_symbols = [STE]
        else:
            stack_push_symbols = list(
                filter(lambda x: x != STE, stack_push_symbols))
        self.stack_push_symbols = stack_push_symbols
        self.flags = set(flags)

    def __str__(self):
        return f'{self.node_from} -> {self.node_to} {self.alphabeth_symbol} {self.stack_pop_symbol}/{",".join(self.stack_push_symbols)}'

    def __repr__(self):
        return str(self)

    def __eq__(self, o):
        return str(self) == str(o)

    def __hash__(self):
        return len(str(self))

    def st(self):
        return (self.stack_pop_symbol, tuple(self.stack_push_symbols))

    def is_eps(self):
        return self.alphabeth_symbol == ALE

    def is_similar(self, o):
        if self.alphabeth_symbol == ALE or o.alphabeth_symbol == ALE:
            return self.stack_pop_symbol != o.stack_pop_symbol
        return self.alphabeth_symbol == o.alphabeth_symbol and self.stack_pop_symbol == o.stack_pop_symbol


class PDA:
    def __init__(self, ast):
        self.raw_ast = ast
        self.nodes = set()
        self.inits = set()
        self.finals = set()
        self.traps = set()
        self.transits = set()
        self.labels = {}
        self.alphabeth = set()
        self.stack_alphabeth = set()

        self.process_ast(ast)
        # print('SELF ALLPHABETH', self.alphabeth)

        self.build_alphahbeths()
        assert self.alphabeth and self.stack_alphabeth

        self.find_traps()

        self.deal_with_eps_and_any()

        # # print('EDGES AFTER DEALING')
        # # for t in self.transits:
        # #     print(t)

        self.find_deterministic_transits()

        self.bring_together_stack_independend_transits()
        self.bring_together_stack_independend_transits2()

    def process_ast(self, ast):
        for block in ast:
            if block[0] == 'single_node_description':
                block = block[1]
                node_id = block['id']
                self.nodes.add(node_id)

                node_label = block['label']
                if node_label is not None:
                    self.labels[node_id] = node_label

                flags = set(block['flags'])
                if ('final_flag',) in flags:
                    self.finals.add(node_id)
                if ('initial_flag',) in flags:
                    self.inits.add(node_id)
                # if ('trap_flag', ) in flags:
                #     self.traps.add(node_id)
                for transit in block['transits']:
                    transit_obj = Transit(
                        node_from=node_id,
                        node_to=transit['dest_id'],
                        alphabeth_unit=transit['alphabeth_unit'],
                        stack_pop_symbol=transit['stack_pop_symbol'],
                        stack_push_symbols=transit['stack_push_symbols'],
                        flags=transit['flags']
                    )
                    self.transits.add(transit_obj)
            elif block[0] == 'single_transit_description':
                block = block[1]
                transit_obj = Transit(
                    node_from=block['node_from'],
                    node_to=block['node_to'],
                    alphabeth_unit=block['alphabeth_unit'],
                    stack_pop_symbol=block['stack_pop_symbol'],
                    stack_push_symbols=block['stack_push_symbols'],
                    flags=block['flags']
                )
                self.nodes.add(block['node_from'])
                self.nodes.add(block['node_to'])
                self.transits.add(transit_obj)

            elif block[0] == 'group_of_nodes':
                block = block[1]
                flags = set(block['flags'])
                self.nodes.update(block['nodes'])
                if ('final_flag',) in flags:
                    self.finals.update(block['nodes'])
                if ('initial_flag',) in flags:
                    self.inits.update(block['nodes'])

                # if ('trap_flag', ) in flags:
                #     self.traps.update(block['nodes'])
            elif block[0] == 'alphabeth':
                for x in block[1]:
                    self.alphabeth.add(x[1])
            elif block[0] == 'stack_alphabeth':
                for x in block[1]:
                    self.stack_alphabeth.add(x[1])

    def find_traps(self):
        not_traps = deepcopy(self.finals)
        while True:
            new_not_traps = set()
            for nt in not_traps:
                new_not_traps |= set(map(lambda x: x.node_from, filter(
                    lambda x: x.node_to in not_traps, self.transits)))
            if new_not_traps.difference(not_traps):
                flag = True
                not_traps |= new_not_traps
            else:
                break
        self.traps = self.nodes.difference(not_traps)

    def build_alphahbeths(self):
        self.alphabeth.update(set(filter(lambda x: x != ALE and x != ALA, map(
            lambda x: x.alphabeth_symbol, self.transits))))

        self.stack_alphabeth.update(
            set(map(lambda x: x.stack_pop_symbol, self.transits)))
        for x in self.transits:
            self.stack_alphabeth.update(x.stack_push_symbols)
        self.stack_alphabeth = set(
            filter(lambda x: x != STA and x != STE, self.stack_alphabeth))

        # print('ALPHABETHS:', self.alphabeth, self.stack_alphabeth)

    def deal_with_eps_and_any(self):
        pass
        # избавимся от всяких eps и any

        # заменим все <qi, any, Sj> -> <qk, Sl>
        # нам множество переходов по конкретной букве
        for t in deepcopy(self.transits):
            if t.alphabeth_symbol == ALA:
                self.transits.discard(t)
                for alpha in self.alphabeth:
                    c = deepcopy(t)
                    c.alphabeth_symbol = alpha
                    self.transits.add(c)
        # такие: <qi, eps, Sj> -> <qk, Sl> мы не трогаем(

        # теперь разберемся со stack_eps
        for t in deepcopy(self.transits):
            if t.stack_pop_symbol == STE:
                self.transits.discard(t)
                for salpha in self.stack_alphabeth:
                    c = deepcopy(t)
                    c.stack_pop_symbol = salpha
                    if c.stack_push_symbols == [STE]:
                        c.stack_push_symbols = [salpha]
                    else:
                        c.stack_push_symbols.append(salpha)
                    self.transits.add(c)

        # # и, наконец, stack_any
        for t in deepcopy(self.transits):
            self.transits.discard(t)
            for salpha in self.stack_alphabeth:
                c = deepcopy(t)
                if c.stack_pop_symbol == STA:
                    c.stack_pop_symbol = salpha
                c.stack_push_symbols = list(
                    map(lambda x: salpha if x == STA else x, c.stack_push_symbols))
                self.transits.add(c)

    def find_deterministic_transits(self):
        self.deterministic_transits = set()

        # print('&&&&&&&&&&&&&&&&&&&&')
        # print('РАЗБИРЕМСЯ С DETERMINISTIC')
        # для каждого узла
        for node in self.nodes:
            # print("НОДА", node)
            # найдем все переходы из этого узла
            transits = set(
                filter(lambda x: x.node_from == node, self.transits))
            # print("ТРАНСИТЫ", transits)
            for t in transits:
                similars = set(map(lambda x: x.is_similar(t), transits))
                # print('ТРАНЗИТ', t, similars)
                # print('ПОХОЖИХ', len(similars))
                if len(set(filter(lambda x: x.is_similar(t), transits))) == 1:
                    self.deterministic_transits.add(t)

        # print('DETERMINISTICS')
        # for x in self.deterministic_transits:
        #     print(x)

    def loop(self, assembled, transits_set, rest_stack_aphabeth):
        rest_stack_aphabeth = deepcopy(rest_stack_aphabeth)
        if not rest_stack_aphabeth:
            # если набор пуст, то ладно
            if not assembled:
                return

            # проверим, что они все одинаковое количество символов кладут на стек
            lengths = set(map(lambda x: len(x.stack_push_symbols), assembled))
            if len(lengths) != 1:
                return

            # а можно этот момент как-то нормально сделать?(((((
            el = assembled.pop()
            assembled.add(el)

            iski = set()
            for i in range(len(el.stack_push_symbols)):
                i_symbols = set(
                    map(lambda x: x.stack_push_symbols[i], assembled))
                if len(i_symbols) == 1:
                    continue
                else:
                    iski.add(i)
                    for t in assembled:
                        if t.stack_pop_symbol != t.stack_push_symbols[i]:
                            return

            # итак,
            # мы получили набор переходов вида <q1,a, Si> -> <q2, f(Si)>,
            # где Si пробегает все эл-ты множества стековых символов ровно по одному разу
            # и где f(x) - последовательность стековых символов, параметризованная стековым символом икс
            # короче, все последовательности стековых символов, кторые вот эти переходы из assembled кладут на стек,
            # отличаются только в i-х позициях, причём, в этих же i-х позициях они имеют символ, который сняли со стека

            self.to_delete_transits |= assembled
            el = deepcopy(el)
            el.stack_pop_symbol = STA
            for i in iski:
                el.stack_push_symbols[i] = STA

            if any(map(lambda x: x in self.deterministic_transits, assembled)):
                self.deterministic_transits.add(el)

            self.transits.add(el)
            return

        another_stack_symbol = rest_stack_aphabeth.pop()
        transits = set(filter(lambda x: x.stack_pop_symbol ==
                                        another_stack_symbol, transits_set))
        # если транзитов по какому-то стековому символу нет, то any мы никак не наберем
        if not transits:
            return
        for t in transits:
            self.loop(
                deepcopy(assembled) | {t},
                transits_set,
                deepcopy(rest_stack_aphabeth)
            )

    def bring_together_stack_independend_transits(self):
        self.to_delete_transits = set()
        for node in self.nodes:
            for node2 in self.nodes:
                for alpha in self.alphabeth | set([ALE]):
                    # найдем все переходы из этого узла по конкретной букве
                    transits = set(filter(
                        lambda x: x.node_from == node and x.node_to == node2 and x.alphabeth_symbol == alpha,
                        self.transits))

                    # if not transits:
                    # continue
                    self.loop(set(), transits, self.stack_alphabeth)

        self.transits = self.transits.difference(self.to_delete_transits)

    def bring_together_stack_independend_transits2(self):
        self.to_delete_transits = set()
        for node in self.nodes:
            for node2 in self.nodes:
                transits = set(filter(
                    lambda x: x.node_from == node and x.node_to == node2 and x.alphabeth_symbol != ALE, self.transits))
                stack_variants = set(map(lambda x: x.st(), transits))
                # print('PAIR', node, node2, stack_variants)
                for variant in stack_variants:
                    suitables = set(filter(lambda x: x.st() == variant, transits))
                    # print('->>>>', suitables)
                    if len(suitables) == len(self.alphabeth):
                        tr = suitables.pop()
                        suitables.add(tr)
                        tr = deepcopy(tr)
                        tr.alphabeth_symbol = ALA
                        self.transits.add(tr)
                        self.transits = self.transits.difference(suitables)
                        if all(map(lambda x: x in self.deterministic_transits, suitables)):
                            self.deterministic_transits.add(tr)

        self.transits = self.transits.difference(self.to_delete_transits)

    def get_graphviz_notation(self):
        lp = '{'
        rp = '}'
        quote = '"'
        nl = '\n'
        strings = set()
        strings.update([
            f'{node};'
            for node in self.nodes
        ])
        strings.update([
            f'{node} [label="{label}"];'
            for node, label in self.labels.items()
        ])
        strings.update([
            f'{node} [color="green"];'
            for node in self.inits
        ])
        strings.update([
            f'{node} [fontcolor="red"];'
            for node in self.traps
        ])
        for transit in self.transits:
            ids = f'{transit.node_from} -> {transit.node_to}'
            if ("stack_independency_flag",) in transit.flags:
                optional = f"arrowhead={quote}dot{quote}"
            else:
                optional = f'label="{transit.alphabeth_symbol}, [{transit.stack_pop_symbol}/{",".join(transit.stack_push_symbols)}]"'
            if transit in self.deterministic_transits:
                optional += ' penwidth="2.5"'
            strings.add(f'{ids} [{optional}]')
        return f'''
        digraph G {lp}
            {f"node [shape = doublecircle]; {', '.join([quote + node + quote for node in self.finals])};" if self.inits else ''}
            node [shape = oval];

            {(nl + '    ').join(strings)}

            label="
            green border means initial state
            red font means trap state
            dot-arrow means stack independency
            bold arrow means deterministic
            "
        {rp}
        '''
