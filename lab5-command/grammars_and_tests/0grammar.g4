@@grammar::PDA
@@parseinfo :: True

start = stmts $ ;
stmts = {stmt}* ;
stmt = {single_edge_description | single_node_description | group_of_nodes} statement_separator ;
statement_separator = ';' ;

node_ids = {node_id}* ;
node_from = node_id ;
node_to = node_id ;

flag = | initial_flag | final_flag;

alphabeth_unit = | eps_symbol | any_symbol| alphabeth_symbol ;

# Все, что ниже этой строчки можно модифицировать

# Символы стека
stack_pop_symbol = stack_unit ;
stack_push_symbol = stack_unit ;
stack_unit = | stack_any | stack_symbol | stack_eps ;

# Строковые литералы
string_literal_1 = {/[a-z0-9_]/}+ ;
string_literal_2 = {/[a-z0-9_]/}+ ;
string_literal_3 = {/[a-z0-9_]/}+ ;
string_literal_4 = {/[a-z0-9_]/}+ ;
string_literal_5 = {/[a-z0-9_]/}+ ;
string_literal_6 = {/[a-z0-9_]/}+ ;
string_literal_7 = {/[a-z0-9_]/}+ ;

# Узлы
node_id = string_literal_1 ;
node_label = string_literal_1 ;

# Внешний алфавита
eps_symbol = '_EPSALPHA' ;
any_symbol = '_ANYALPHA' ;
alphabeth_symbol = /[a-z]/ ;

# Стек
stack_symbol = {/[A-Z]/}+{/[0-9]/}* ;
stack_any = "_ANYSTACK" ;
stack_eps = '_EPSSTACK' ;

# Флаги узлов
initial_flag = 'is_initial' ;
final_flag = 'is_final' ;

# Логические блоки
single_node_description = 
    'node'
    node_id 
    ['(' {flag | "label" "=" '"' node_label '"'}+')' ]
    ['{' single_node_transits '}']
    ;

single_node_transits = {single_node_transit}+;

single_node_transit = '(' node_id alphabeth_unit stack_pop_symbol '/' {stack_push_symbol ','}* stack_push_symbol')';

single_edge_description = 'edge' node_from '->' node_to alphabeth_unit 
                '[' stack_pop_symbol '/' {stack_push_symbol ','}* stack_push_symbol ']' ;

group_of_nodes = 'group' '(' {flag ',' }* flag ')' '{' {node_id}+ '}' ;