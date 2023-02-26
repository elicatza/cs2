#!/usr/bin/env python3.10

from typing import TypedDict, Callable
import datetime as dt
import argparse
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
    parser = argparse.ArgumentParser(description='Make cat observations!!',
                                     prefix_chars='--',
                                     allow_abbrev=True)
    parser.add_argument('-l', '--list',
                        action='store_true',
                        required=False,
                        help='List all observed cats')
    parser.add_argument('-a', '--add',
                        action='store_true',
                        required=False,
                        help='Add new cat')

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


class Cats:
    def __init__(self, cats: list[CatInfo]):
        self.cats = cats

    def display(self) -> None:
        for cat in self.cats:
            print(f"type : {cat['type']}")
            print(f"Place: {cat['place']}")
            print(f"Count: {cat['count']}")
            for time, obser in zip(cat['times'], cat['observations']):
                print(f'{time}: {obser}')
            print('')  # newline

        return None

    def get_cat_index(self, type: str, place: str) -> int:
        for i, cat in enumerate(self.cats):
            if cat['type'] == type and cat['place'] == place:
                return i
        # print(next(index for index, item in enumerate(cats) if item['type'] == place))
        return -1

    def add_new_cat(self, type: str, place: str, observation: str) -> None:
        self.cats.append(
                CatInfo(place=place,
                        type=type,
                        count=1,
                        times=[str(dt.datetime.now())],
                        observations=[observation]
                        ))
        return None

    def mutate_cat(self, type: str, place: str, observation: str, id: int) -> None:
        if id < 0:
            return None
        # print(next(index for index, item in enumerate(cats) if item['type'] == place))
        self.cats[id]['times'].append(str(dt.datetime.now()))
        self.cats[id]['observations'].append(observation)
        self.cats[id]['count'] += 1

        return None


def main() -> None:
    args = get_arg_namespace()

    cats = Cats(parse_cat_file(FILENAME))

    if args.list:
        cats.display()

    if args.add:
        # Get user input cat
        cat_type = friendly_input("Enter cat type: ", str, "ERROR: Not a valid cat type")
        cat_place = friendly_input("Enter place: ", str, "ERROR: Not a valid place")
        cat_obser = friendly_input("Enter observation: ", str, "ERROR: Not a valid observation")

        cat_id = cats.get_cat_index(cat_type, cat_place)
        if cat_id >= 0:
            cats.mutate_cat(cat_type, cat_place, cat_obser, cat_id)
        else:
            cats.add_new_cat(cat_type, cat_place, cat_obser)

        write_cat_file(FILENAME, cats.cats)

    return None


if __name__ == '__main__':
    main()
