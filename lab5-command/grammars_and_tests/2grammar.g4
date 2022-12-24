@@grammar::PDA
@@parseinfo :: True

start = stmts $ ;

stmts = {stmt}* ;

stmt = {single_edge_description | single_node_description | group_of_nodes} statement_separator ;

single_node_description = node_id '(' {flag | key_word1 node_label | node_label }* ')' ;

single_edge_description = 'pass';

group_of_nodes = 'pass' ;

flag = | initial_flag | final_flag | trap_flag;
initial_flag = 'is_initial' ;
final_flag = 'is_final' ;
trap_flag = 'is_trap' ;


node_id = string_literal_1 ;
node_label = string_literal_2 ;

statement_separator = ';' ;
key_word1 = | 'label=' | 'label:' | 'label' ;
key_word2 = | 'id=' | 'id' ;

string_literal_1 = {/[a-z0-9_]/}+ ;
string_literal_2 = {/[a-z0-9_]/}+ ;
string_literal_3 = {/[a-z0-9_]/}+ ;
string_literal_4 = {/[a-z0-9_]/}+ ;
string_literal_5 = {/[a-z0-9_]/}+ ;
string_literal_6 = {/[a-z0-9_]/}+ ;
string_literal_7 = {/[a-z0-9_]/}+ ;