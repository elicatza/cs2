#!/usr/bin/env python3
import sys
import argparse
from typing import TypedDict, Iterable
import json


class Pc(TypedDict):
    uid: str
    purchased: int
    type: str


# Reads json file, and decode pcs
def fetch_pcs() -> list[Pc]:
    with open("./pcs.json", 'r') as fp:
        pcs: list[Pc] = json.load(fp)

    return pcs


# Parse string to Pc
def parse_pc(pc: str) -> Pc | None:
    if len(pc.split(' ', maxsplit=2)) != 3:
        return None

    year = pc.split(' ', maxsplit=2)[0]
    uid = pc.split(' ', maxsplit=2)[1]

    if not year.isnumeric():
        return None
    year_int = int(year)

    # Check if last 4 chars of uid is numeric
    if not uid[-4:].isnumeric():
        return None

    if uid[-6:-4] != 'NB' and uid[-6:-4] != 'PC':
        return None

    type = pc.split(' ', maxsplit=2)[2]

    return {'uid': uid, 'purchased': year_int, 'type': type}


# Checks if pc has an uid
def has_uid(pc: Pc, pcs: Iterable[Pc]) -> bool:
    matches = tuple(filter(lambda item: item['uid'] == pc['uid'], pcs))

    if matches:
        return False

    return True


# Writes json to file
def write_pcs(pcs: Iterable[Pc]) -> bool:
    with open("./pcs.json", 'w') as fp:
        json.dump(pcs, fp, indent=4)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description='Register Pcs', prefix_chars='--', allow_abbrev=True)
    parser.add_argument('-a', '--add', metavar='PC', type=str, help='add pc i.e: `2020 KOVNB0111 lenovo E495`')
    parser.add_argument('-l', '--list', action='store_true', help='Lists all PCs in system')

    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    args = parser.parse_args()

    if args.add is not None:
        pc = parse_pc(args.add)
        if pc is not None:
            pcs = fetch_pcs()
            if has_uid(pc, pcs):
                pcs.append(pc)
                write_pcs(pcs)
            else:
                print("Duplicate pc!")
                print("Duplicate pcs not allowed. Exiting...")
                sys.exit(0)
        else:
            print("Not a valid pc!")
            print("Has to be in format: `2020 KOVNB0111 lenovo E495`")
            sys.exit(0)

    if args.list:
        print(json.dumps(fetch_pcs(), indent=4))


if __name__ == '__main__':
    main()
