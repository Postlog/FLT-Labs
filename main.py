from models import RegexParser, Node, NodeType, Regex
from copy import deepcopy
from executor import execute
from logger import logger
# from derivative.derivative_utils import DerivativeBrzozovski, derivative_regex_antimirov, tree_to_regex
from derivative.derivatives import derivative_regex_antimirov, derivative_regex_brzozovski
from derivative.utils import tree_to_regex
from functions.pumping_length import PumpingLength

def main():
    try:
        execute()
    except Exception as e:
        logger.error(f'Произошла непредвиденная ошибка: {e}')


if __name__ == '__main__':
    # main()
    print('Введите регулярное выражение: ')
    string = input()
    print('Введите дифференциал для Брзозовски: ')
    differential_br = input()
    print('Введите дифференциал для Антимирова: ')
    differential_an = input()

    tree = RegexParser.parse(string)
    regex = Regex(tree, string)

    print('Производная Брзозовски: ')
    brzozovski_der = tree
    for symbol in differential_br:
        brzozovski_der = derivative_regex_brzozovski(symbol, brzozovski_der)
    print(tree_to_regex(brzozovski_der))
    print('Производная Антимирова: ')
    antimirov_der = derivative_regex_antimirov(tree, differential_an)
    print(antimirov_der)
    # print('Длина накачки: ')
    # length = PumpingLength(regex)
