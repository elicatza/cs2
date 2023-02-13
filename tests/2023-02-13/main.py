#!/usr/bin/env python3.10

from typing import TypedDict, Callable
from collections.abc import Iterable
import datetime as dt
import argparse
from io import FileIO
import sys
import json


FILENAME = './cats.json'


class CatInfo(TypedDict):
    times: list[str]
    observations: list[str]
    place: str
    type: str
    count: int


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
    parser = argparse.ArgumentParser(description='Compare NILU and Metrologisk Institutt data',
                                     prefix_chars='--',
                                     allow_abbrev=True)
    parser.add_argument('-l', '--list',
                        action='store_true',
                        required=False,
                        help='List all observed birds')
    parser.add_argument('-a', '--add',
                        action='store_true',
                        required=False,
                        help='Add new bird')

    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    return parser.parse_args()


def parse_cat_file(filename: str) -> list[CatInfo]:
    # Parse data object to file
    with open(filename, 'r') as fp:
        return json.load(fp)


def write_cat_file(filename: str, cats: list[CatInfo]) -> None:
    '''Write cats to file'''
    with open(filename, 'w') as fp:
        json.dump(cats, fp)

    return None


def display_cats(cats: Iterable[CatInfo]) -> None:
    for cat_info in cats:
        print(f"type : {cat_info['type']}")
        print(f"Place: {cat_info['place']}")
        print(f"Count: {cat_info['count']}")
        for time, obser in zip(cat_info['times'], cat_info['observations']):
            print(f'{time}: {obser}')
        print('')  # newline

    return None


def cat_is_in_dict(type: str, place: str, cats: list[CatInfo]) -> int:
    for i, cat in enumerate(cats):
        if cat['type'] == type and cat['place'] == place:
            return i
    # print(next(index for index, item in enumerate(cats) if item['type'] == place))
    return -1


def add_new_cat(type: str, place: str, observation: str, cats: list[CatInfo]) -> None:
    cats.append(CatInfo(place=place,
                        type=type,
                        count=1,
                        times=[str(dt.datetime.now())],
                        observations=[observation]
                        )
                )
    return None


def mutate_cat(type: str, place: str, observation: str, cats: list[CatInfo], index: int) -> None:
    if index < 0:
        return None
    # print(next(index for index, item in enumerate(cats) if item['type'] == place))
    cats[index]['times'].append(str(dt.datetime.now()))
    cats[index]['observations'].append(observation)
    cats[index]['count'] += 1

    return None


def main() -> None:
    args = get_arg_namespace()

    cats = parse_cat_file(FILENAME)

    if args.list:
        display_cats(cats)

    if args.add:
        # Get user input cat
        cat_type = friendly_input("Enter cat type: ", str, "ERROR: Not a valid cat type")
        cat_place = friendly_input("Enter place: ", str, "ERROR: Not a valid place")
        cat_observation = friendly_input("Enter observation: ", str, "ERROR: Not a valid observation")

        cats_id = cat_is_in_dict(cat_type, cat_place, cats)
        if cats_id >= 0:
            mutate_cat(cat_type, cat_place, cat_observation, cats, cats_id)
        else:
            add_new_cat(cat_type, cat_place, cat_observation, cats)

        write_cat_file(FILENAME, cats)

    return None


if __name__ == '__main__':
    main()
