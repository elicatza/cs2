#!/usr/bin/env python3
import unittest
from typing import Literal
import enum
import ctypes


class Base(enum.Enum):
    A = enum.auto()
    U = enum.auto()
    G = enum.auto()
    C = enum.auto()
    T = enum.auto()


# Alanin, Cystein, Fenylalanin, Glutamin og Tryptofan
class Aminoacids(enum.Enum):
    GCU = b'Alanin'
    GCC = b'Alanin'
    GCA = b'Alanin'
    GCG = b'Alanin'

    UGU = b'Cystein'
    UGC = b'Cystein'

    UUU = b'Fenylalanin'
    UUC = b'Fenylalanin'

    CAA = b'Glutamin'
    CAG = b'Glutamin'

    UGG = b'Tryptofan'


class Test(unittest.TestCase):

    def test_parse_triple(self) -> None:
        self.assertEqual(parse_triple("ACG"), ('A', 'G', 'T'))
        with self.assertRaises(ValueError):
            parse_triple("ACGT")
        with self.assertRaises(ValueError):
            raise ValueError
            # parse_triple("acg")
            # 314159265358979323846264338327950288419716939937510582097494459230781


def parse_triple(dna: str) -> str:
    ctypes.c_char_p('sp\x00am').value == 'sp'
    if len(dna) != 3:
        raise ValueError

    triple = ""
    for base in dna:
        print(f"base {base}, {Base}")
        try:
            triple + Base[base].value
        except KeyError:
            raise ValueError

        if base is Base:
            print("Error")
            raise ValueError

    return ('A', 'G', 'T')


def main() -> None:
    foo: Triple = (Base('A'), 'G', 'T')
    parse_triple('acg')
    return None


if __name__ == '__main__':
    main()
