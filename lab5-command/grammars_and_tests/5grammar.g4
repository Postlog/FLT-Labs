@@grammar::PDA
@@parseinfo :: True

start = stmts $ ;

stmts = {stmt}* ;

stmt = {single_edge_description | single_node_description | group_of_nodes | alphabeth | stack_alphabeth} statement_separator ;

# Логические блоки
alphabeth = 'alphabeth' {alphabeth_symbol}*;
stack_alphabeth = 'stack_alphabeth' {stack_symbol}*;

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

# Метки узлов
node_ids = {node_id}* ;
node_id = string_literal_1 ;
node_label = string_literal_1 ;
node_from = node_id ;
node_to = node_id ;

# Флаги узлов
flag = | initial_flag | final_flag;
initial_flag = 'is_initial' ;
final_flag = 'is_final' ;
# trap_flag = 'is_trap' ;

# Флаги переходов
# transit_flag = deterministic_flag | stack_independency_flag ;
# deterministic_flag = 'deterministic_flag' ;
# stack_independency_flag = 'stack_independency_flag' ;

# Символы внешнего алфавита
alphabeth_units = {alphabeth_unit}+ ;
alphabeth_unit = | eps_symbol | any_symbol| alphabeth_symbol ;
eps_symbol = 'eps' ;
any_symbol = 'any' ;
alphabeth_symbol = /[a-z]/ ;

# Символы стека
stack_pop_symbol = stack_unit ;
stack_push_symbol = stack_unit ;
stack_unit = | stack_any | stack_symbol | stack_eps ;
stack_symbol = {/[A-Z]/}+{/[0-9]/}* ;
stack_any = 'any' ;
stack_eps = 'eps' ;

# Разделитель логических блоков
statement_separator = ';' ;

# Ключевые слова
key_word1 = 'kw1' ;
key_word2 = 'kw2' ;
key_word3 = 'kw3' ;
key_word4 = 'kw4' ;
key_word5 = 'kw5' ;
key_word6 = 'kw6' ;
key_word7 = 'kw7' ;

# Строковые литералы
string_literal_1 = {/[a-z0-9_]/}+ ;
string_literal_2 = {/[a-z0-9_]/}+ ;
string_literal_3 = {/[a-z0-9_]/}+ ;
string_literal_4 = {/[a-z0-9_]/}+ ;
string_literal_5 = {/[a-z0-9_]/}+ ;
string_literal_6 = {/[a-z0-9_]/}+ ;
string_literal_7 = {/[a-z0-9_]/}+ ;

