#!/usr/bin/env python

import json
from typing import NamedTuple
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

DATAF_F_NAME = './data.json'


# 'Papiravis', 'Fjernsyn', 'Radio', 'Bøker', 'Internett', 'Digitale spill'
class Data(NamedTuple):
    year: int
    data: dict[str, int]


def main() -> None:
    with open(DATAF_F_NAME, 'r', encoding='utf-8') as fp:
        raw_data = json.load(fp)

    categories = tuple(raw_data['dataset']['dimension']['Media']['category']['label'].values())
    years = tuple(map(int, raw_data['dataset']['dimension']['Tid']['category']['index']))
    values = np.array_split(np.array(raw_data['dataset']['value']), len(categories))

    data: deque[Data] = deque()
    cats = {}
    for i in range(len(years)):
        for j, category in enumerate(categories):
            if values[j][i] is None:
                cats[category] = 0
            else:
                cats[category] = values[j][i]

        data.append(Data(year=years[i], data=cats))
        cats = {}

    fig, ax = plt.subplots()

    for i, val in enumerate(data):
        ax.clear()
        ax.grid(axis='y')
        ax.bar(categories, val.data.values())
        ax.set_ylabel('Bruk in minutter')
        ax.set_ylim((0, 250))
        ax.set_title(f'År: {val.year}')
        plt.pause(0.5)

    plt.show()


if __name__ == '__main__':
    main()
