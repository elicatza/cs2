#!/usr/bin/env python3.10

from collections import deque
from collections.abc import Generator
from typing import TypedDict, Any
import argparse
import datetime as dt
import json
import matplotlib.dates as mdate
import matplotlib.pyplot as plt
import math
import requests as req
import sys
import numpy as np
import numpy.typing as npt


class Location(TypedDict):
    name: str
    lati: float
    long: float


class LocationData(TypedDict):
    location: Location

    # Metrologisk Institutt
    temperature: float  # degrees
    pressure: float     # at sea level
    humidity: float     # percent relative
    cloud: float        # percent
    wind_speed: float   # m / s

    # Nilu
    pm10: float  # 0 - 600 μg/m^3


class BigData(TypedDict):
    time: str
    location_data: list[LocationData]


HEADERS = {
    'Content-type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'User-Agent': 'Python/3.10.9'
}


def get_url_json(url: str, headers: dict[str, str]) -> Any:
    res = req.get(url, headers=headers)
    if res.status_code != 200:
        print(f"ERROR: invalid status code from `{url}`", file=sys.stderr)
        raise req.ConnectionError

    return json.loads(res.text)


def fetch_location_data() -> Generator[LocationData, None, None]:
    # API docs: https://api.nilu.no/
    nilu_url = "https://api.nilu.no/aq/utd?areas=oslo&components=pm10"
    nilu_data = get_url_json(nilu_url, headers=HEADERS)

    for place in nilu_data:
        # API docs: https://api.met.no/weatherapi/locationforecast/2.0/documentation
        met_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}"
        met_url = met_url.format(place['latitude'], place['longitude'])
        met_data = get_url_json(met_url, headers=HEADERS)
        met_pdata = met_data['properties']['timeseries'][0]['data']['instant']['details']

        yield LocationData(
                location=Location(name=place['station'],
                                  lati=place['latitude'],
                                  long=place['longitude']
                                  ),
                temperature=met_pdata['air_temperature'],
                pressure=met_pdata['air_pressure_at_sea_level'],
                humidity=met_pdata['relative_humidity'],
                cloud=met_pdata['cloud_area_fraction'],
                wind_speed=met_pdata['wind_speed'],
                pm10=place['value'])


def get_arg_namespace() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Compare NILU and Metrologisk Institutt data',
                                     prefix_chars='--',
                                     allow_abbrev=True)
    parser.add_argument('-f', '--fetch',
                        action='store_true',
                        required=False,
                        help='fetch data and print to stdout')
    parser.add_argument('-F', '--file',
                        type=argparse.FileType('r'),
                        required=False,
                        default='/var/local/climate_data/data.json',
                        help='choose which file to read data from')

    return parser.parse_args()


def calculate_linearity(x: npt.NDArray[np.float32], y: npt.NDArray[np.float32]) -> float:
    size = len(x)
    if size != len(y):
        return 0

    # i: inner multiply
    # o: outer multiply
    sumxi = np.sum(x * x)
    sumxo = np.sum(x) ** 2
    sx = sumxi - (sumxo / size)

    sumyi = np.sum(y * y)
    sumyo = np.sum(y) ** 2
    sy = sumyi - (sumyo / size)

    sumxyi = np.sum(x * y)
    sumxyo = np.sum(x) * np.sum(y)
    sxy = sumxyi - (sumxyo / size)

    return float(sxy / (math.sqrt(sx) * math.sqrt(sy)))


def main() -> None:
    args = get_arg_namespace()

    if args.fetch:
        location_data = list(fetch_location_data())
        print(json.dumps(BigData(location_data=location_data, time=str(dt.datetime.now()))))

        return None

    data_deq: deque[BigData] = deque()
    for row in args.file:
        data_deq.append(json.loads(row))

    time: deque[str] = deque(maxlen=len(data_deq))
    pm10: deque[float] = deque(maxlen=len(data_deq))
    wind_speed: deque[float] = deque(maxlen=len(data_deq))
    pressure: deque[float] = deque(maxlen=len(data_deq))

    for big_data in data_deq:
        time.append(big_data['time'])
        for i in big_data['location_data']:
            if i['location']['name'] == 'Spikersuppa':
                pm10.append(i['pm10'])
                wind_speed.append(i['wind_speed'])
                pressure.append(i['pressure'])

    for i, t in enumerate(time):  # type: ignore
        time[i] = dt.datetime.fromisoformat(t)  # type: ignore
        # print(time[i], pm10[i], wind_speed[i])  # type: ignore

    zero = mdate.date2num(time[0])
    fig, ax = plt.subplots()
    xax = np.arange(0, len(time), dtype=np.int32)

    # Numpy has builtin np.corrcoef, but i wanted to to it myself
    # print(np.corrcoef(np.array(pm10), np.array(wind_speed)))
    r = calculate_linearity(np.array(pm10), np.array(pressure))
    print(f"pm10, pressure corr: {r}")

    ax.bar(xax, wind_speed)
    ax.bar(xax, pm10)
    # ax.set_ylabel('Bruk in minutter')
    # ax.set_ylim((0, 250))
    # ax.set_title(f'År: {val.year}')
    plt.show()

    return None


if __name__ == '__main__':
    main()
