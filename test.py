from models.regex import RegexParser, Regex
from models import FiniteAutomaton, FiniteAutomatonIndexed
from functions.thompson import Thompson



if __name__ == "__main__":
    st = "ad|(b*|(ac)*)"
    c = RegexParser.parse(st)

    finite_automata = Thompson(Regex(c,st))

    print(finite_automata)