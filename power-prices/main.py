#!/usr/bin/env python

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

TEMPERATURE_F_NAME = "temp.txt"
POWER_PRICE_F_NAME = "power_prices.txt"
DAYS_BUF_SIZE = 31


def read_file_data(pathname: str, size: int) -> npt.NDArray[np.float32]:
    buffer = np.zeros(DAYS_BUF_SIZE, dtype=np.float32)
    with open(pathname, 'r', encoding='utf-8') as fp:
        for i in range(size):
            buffer[i] = np.float32(fp.readline())

    return buffer


def main() -> None:
    time = np.arange(DAYS_BUF_SIZE)
    temperatures = read_file_data(TEMPERATURE_F_NAME, DAYS_BUF_SIZE)
    prices = read_file_data(POWER_PRICE_F_NAME, DAYS_BUF_SIZE) / 100

    fig, ax = plt.subplots()

    ax.barh(time + 0.2, temperatures, height=0.4)
    ax.barh(time - 0.2, prices, height=0.4)
    ax.set_title('Strømpriser samenlignet med temperatur for desember 2022')
    ax.set_ylabel('Dager')

    plt.show()


if __name__ == '__main__':
    main()
