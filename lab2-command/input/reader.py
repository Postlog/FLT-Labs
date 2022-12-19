import sys


def read() -> str:
    raw_input = ''

    for line in sys.stdin:
        raw_input += line

    return raw_input
