#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

VALG_DATA_F = "./valgdeltagelse.txt"
DATAPOINTS = 20


def main() -> None:
    time = np.zeros(DATAPOINTS, dtype=np.int32)
    vote = np.zeros(DATAPOINTS, dtype=np.float32)

    with open(VALG_DATA_F, 'r', encoding='utf-8') as fp:
        for i in range(DATAPOINTS):
            line = fp.readline().strip().replace(',', '.')
            time[i] = np.float32(line.split(';')[0])
            vote[i] = np.float32(line.split(';')[1])

    fig, ax = plt.subplots()

    ax.bar(time, vote, width=2.5, color='#55cdfc', label='wowie')
    ax.grid(axis='y')
    ax.set_title('Valgoppsluttning fra 1945 til 2021')
    ax.set_xlabel('Tid i år')
    ax.set_ylabel('Valgdeltagelse i prosent')
    ax.set_ylim((50, 100))

    plt.show()


if __name__ == '__main__':
    main()
