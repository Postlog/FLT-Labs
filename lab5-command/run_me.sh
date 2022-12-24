tatsu  --generate-parser "grammars_and_tests/$1grammar.g4" > parser.py && python main.py $1 && dot -Tsvg graph.dot > graph.svg
