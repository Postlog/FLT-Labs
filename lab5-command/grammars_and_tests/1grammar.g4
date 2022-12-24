@@grammar::PDA
@@parseinfo :: True

start = stmts $ ;

stmts = {stmt}* ;

stmt = {single_edge_description | single_node_description | group_of_nodes} statement_separator ;

single_node_description =  
    "'" node_id "'" 
    ['(' {flag | {"label=" | "label:" | key_word1} '"' node_label '"'}* ')']
    [ single_node_transits ]
;

single_node_transits = {lp1 single_node_transit rp1}* ;
single_node_transit = node_id alphabeth_unit stack_pop_symbol '/' stack_push_symbols ;

single_edge_description = 'edge' ;
group_of_nodes = 'group' ;

node_id = string_literal_1 ;
node_label = string_literal_2 ;


flag = | initial_flag | final_flag | trap_flag;
initial_flag = 'is_initial' ;
final_flag = 'is_final' ;
trap_flag = 'is_trap' ;


alphabeth_units = {alphabeth_unit}+ ;
alphabeth_unit = | eps_symbol | alphabeth_symbol ;
eps_symbol = 'eps' ;
alphabeth_symbol = /[a-z]/ ;

stack_pop_symbol = stack_unit ;
stack_push_symbols = stack_units ;
stack_units = {stack_unit}+ ;
stack_unit = | stack_any | stack_symbol | stack_eps ;
stack_symbol = {/[A-Z]/}+{/[0-9]/}* ;
stack_any = 'any' ;
stack_eps = 'eps' ;


separator1 = ',' ;
statement_separator = ';' ;
lp1 = '(' ;
rp1 = ')' ;
key_word1 = 'label' ;
key_word2 = | 'id=' | 'id' ;
arrow = '->';


string_literal_1 = {/[a-z0-9_]/}+ ;
string_literal_2 = {/[a-z0-9_ ]/}+ ;
string_literal_3 = {/[a-z0-9_]/}+ ;
string_literal_4 = {/[a-z0-9_]/}+ ;
string_literal_5 = {/[a-z0-9_]/}+ ;
string_literal_6 = {/[a-z0-9_]/}+ ;
string_literal_7 = {/[a-z0-9_]/}+ ;