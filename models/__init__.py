# from .base import *
# from .bool import *
from models.dfa import DFA
# from .int import *
from models.nfa import NFA
# from .nullable_bool import *
# from .regex import *

if __name__ == "__main__":
    nfa = NFA(
        #тест для детерминизации
        states={'q0', 'q1', 'q2', 'q3'},
        input_symbols={'a', 'b'},
        transitions={
            'q0': {'b': {'q3'}, 'a': {'q1'}, '': {'q2'}},
            'q1': {'': {'q3'}},
            'q2': {'b': {'q1'}},
            'q3': {'a': {'q1'}, '': {'q2'}}
        },
        initial_state='q0',
        final_states={'q3'}


        #тест для минимизации
        # states={'s0', 's1', 's2', 's3', 's4', 's5'},
        # input_symbols={'0', '1'},
        # transitions={
        #     's0': {'0': {'s0'}, '1': {'s1'}},
        #     's1': {'0': {'s2'}, '1': {'s1'}},
        #     's2': {'0': {'s0'}, '1': {'s3'}},
        #     's3': {'0': {'s4'}, '1': {'s3'}},
        #     's4': {'0': {'s5'}, '1': {'s3'}},
        #     's5': {'0': {'s5'}, '1': {'s3'}}
        # },
        # initial_state='s0',
        # final_states={'s3', 's4', 's5'}
    )


    check = NFA.determinize(nfa)
    # check = NFA.minimize(nfa)
    a = 1

