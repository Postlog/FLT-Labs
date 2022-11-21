from models import RegexParser, Node, NodeType
from copy import deepcopy
from executor import execute
from logger import logger


def main():
    try:
        execute()
    except Exception as e:
        logger.error(f'Произошла непредвиденная ошибка: {e}')


if __name__ == '__main__':
    main()
