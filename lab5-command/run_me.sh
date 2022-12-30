tatsu  --generate-parser "grammars_and_tests/$1grammar.g4" > parser.py && python3.10 main.py $1 && dot -Tsvg graph.dot > graph.svg
