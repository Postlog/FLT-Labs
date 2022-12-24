@@grammar::PDA
@@parseinfo :: True

start = stmts $ ;

stmts = {stmt}* ;

stmt = {single_edge_description | single_node_description | group_of_nodes} statement_separator ;

single_node_transits = {single_node_transit}+;

# Метки узлов
node_ids = {node_id}* ;
node_id = string_literal_1 ;
node_label = string_literal_2 ;
node_from = node_id ;
node_to = node_id ;

# Флаги
flag = | initial_flag | final_flag | trap_flag;
initial_flag = 'is_initial' ;
final_flag = 'is_final' ;
trap_flag = 'is_trap' ;
transit_flag = deterministic_flag | stack_independency_flag ;
deterministic_flag = 'deterministic_flag' ;
stack_independency_flag = 'stack_independency_flag' ;

# Символы строки
alphabeth_units = {alphabeth_unit}+ ;
alphabeth_unit = | eps_symbol | alphabeth_symbol ;
eps_symbol = 'eps' ;
alphabeth_symbol = /[a-z]/ ;

# Символы стека
stack_pop_symbol = stack_unit ;
stack_push_symbol = stack_unit ;
stack_unit = | stack_any | stack_symbol | stack_eps ;
stack_symbol = {/[A-Z]/}+{/[0-9]/}* ;
stack_any = 'any' ;
stack_eps = 'eps' ;


statement_separator = ';' ;
key_word1 = 'label' ;
key_word2 = | 'id=' | 'id' ;


string_literal_1 = {/[a-z0-9_]/}+ ;
string_literal_2 = {/[a-z0-9_]/}+ ;
string_literal_3 = {/[a-z0-9_]/}+ ;
string_literal_4 = {/[a-z0-9_]/}+ ;
string_literal_5 = {/[a-z0-9_]/}+ ;
string_literal_6 = {/[a-z0-9_]/}+ ;
string_literal_7 = {/[a-z0-9_]/}+ ;

# --------
single_node_description = 
    'node'
    node_id 
    ['(' {flag | {"label=" | "label:" | key_word1} '"' node_label '"'}*')' ]
    ['{' single_node_transits '}']
    ;


single_node_transit = '(' node_id alphabeth_unit stack_pop_symbol '/' {stack_push_symbol ','}* stack_push_symbol ['(' {transit_flag}* ')' ] ')';

# --------
single_edge_description = 'edge' node_from alphabeth_unit '->' node_to stack_pop_symbol '/' {stack_push_symbol ','}* stack_push_symbol ['(' {transit_flag}* ')' ];

# --------
group_of_nodes = 'group' '(' {{flag | flag flag}* ','}* flag ')' {node_id}+ ;
