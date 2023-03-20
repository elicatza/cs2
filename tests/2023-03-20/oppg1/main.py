#!/usr/bin/env python3.10

from collections.abc import Iterable
from typing import TypedDict, Callable
import argparse
import json
import os
import sys


FILENAME = './remember.json'


class Remember(TypedDict):
    datetime: str
    body: str
    header: str


# Type check function can be builtin python, or function returning var / False,
# depending on if condition is met
def friendly_input(prompt: str, type_check: Callable[[str], str], invalid_message: str) -> str:
    while True:
        try:
            user_input = type_check(input(prompt))
            if user_input is False:
                raise ValueError
            break
        except (EOFError, KeyboardInterrupt):
            exit(0)
        except ValueError:
            print(invalid_message)

    return user_input


def get_arg_namespace() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Enter an item to remember!!',
                                     prefix_chars='--',
                                     allow_abbrev=True)
    parser.add_argument('-l', '--list',
                        action='store_true',
                        required=False,
                        help='List all items')
    parser.add_argument('-a', '--add',
                        action='store_true',
                        required=False,
                        help='Add new thing to remember')

    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    return parser.parse_args()


def parse_remember_file(filename: str) -> list[Remember]:
    # Parse data object to file
    if not os.path.exists(filename):
        os.mknod(filename)
        return []

    if os.path.getsize(filename) == 0:
        return []

    with open(filename, 'r') as fp:
        return json.load(fp)


def write_remember_file(filename: str, items: list[Remember]) -> None:
    '''Write remember items to file'''
    if not os.path.exists(filename):
        os.mknod(filename)

    with open(filename, 'w') as fp:
        json.dump(items, fp)

    return None


def display_remember_items(items: Iterable[Remember]) -> None:
    for item in items:
        print(f"#### {item['header']}")
        print(f"{item['body']}")
        print(f"date: {item['datetime']}")
        print('')  # newline

    return None


def add_new_remember(date: str, header: str, body: str, items: list[Remember]) -> None:
    items.append(Remember(
        datetime=date,
        header=header,
        body=body,
        )
                 )
    return None


def main() -> None:
    args = get_arg_namespace()

    items = parse_remember_file(FILENAME)

    if args.list:
        display_remember_items(items)

    if args.add:
        # Get user input remember
        r_header = friendly_input("Enter header: ", str, "ERROR: Not a valid header type")
        r_body = friendly_input("Enter body: ", str, "ERROR: Not a body type")
        r_date = friendly_input("Enter time: ", str, "ERROR: Not a valid date")

        add_new_remember(r_date, r_header, r_body, items)
        write_remember_file(FILENAME, items)

    return None


if __name__ == '__main__':
    main()
