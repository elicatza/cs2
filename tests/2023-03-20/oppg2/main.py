#!/usr/bin/env python

import matplotlib.pyplot as plt
from typing import Any
import json


FILENAME = './bildata.json'


def parse_remember_file(filename: str) -> list[Any]:
    '''Parse data object'''

    with open(filename, 'r') as fp:
        return json.load(fp)


def main() -> None:
    data_obj = parse_remember_file(FILENAME)

    # Slow: O(4n), but there is not much data, so it doesn't matter
    years = [int(i['year']) for i in data_obj[0]['data']]
    bensin = [int(i['antall']) for i in data_obj[0]['data']]
    disel = [int(i['antall']) for i in data_obj[1]['data']]
    el = [int(i['antall']) for i in data_obj[2]['data']]
    total = list(map(sum, zip(bensin, disel, el)))

    fig, ax = plt.subplots()

    ax.plot(years, bensin, color='#55CDFC', label='Bensin')
    ax.plot(years, disel, color='#F7A8BC', label='Disel')
    ax.plot(years, el, color='#999999', label='Elektrisk')
    ax.plot(years, total, color='#282828', label='Total')
    ax.grid(axis='y')
    ax.set_title('Antall biler fra 2008 til 2022')
    ax.set_xlabel('Tid i år')
    ax.set_ylabel('Antall biler')
    ax.legend(loc="upper left")
    ax.set_ylim((0, 3_000_000))

    plt.show()

    return None


if __name__ == "__main__":
    main()
