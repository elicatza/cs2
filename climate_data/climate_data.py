#!/usr/bin/env python3.10

from collections.abc import Generator, Iterable
from typing import TypedDict, Any
import argparse
import datetime as dt
from io import TextIOWrapper
import json
import matplotlib.pyplot as plt
import requests as req
import sys
import numpy as np
import itertools


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


class EntryObj(TypedDict):
    time: dt.datetime
    location_data: list[LocationData]


HEADERS = {
    'Content-type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'User-Agent': 'Python/3.10.9'
}

PLACES = (
        'Rv 4, Aker sykehus',
        'Smestad',
        'Sofienbergparken',
        'Manglerud',
        'Bygdøy Alle',
        'Alnabru',
        'Skøyen',
        'Hjortnes',
        'Kirkeveien',
        'Spikersuppa',
        'Vahl skole',
        'Loallmenningen',
        'E6 Alna senter',
        'Brynbanen'
        )

DATA_FIELDS = (
        'temperature',
        'pressure',
        'humidity',
        'cloud',
        'wind_speed',
        )


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


def arg_parse_hour(val: str) -> tuple[int, int]:
    start, end = map(int, val.split(':', 2))
    if start >= end:
        raise argparse.ArgumentTypeError('Invalid time. First number is has to be heigher than second number')

    if not (start >= 0 and start <= 23) and (end >= 0 and end <= 23):
        raise argparse.ArgumentTypeError('%s is not a valid time. has to be in range 0-23')

    return (start, end)


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
    parser.add_argument('-w', '--wind-speed',
                        action='store_true',
                        required=False,
                        help='show plot for wind speed')
    parser.add_argument('-t', '--time',
                        type=arg_parse_hour,
                        required=False,
                        default=(12, 13),
                        help='specify time range')
    parser.add_argument('-p', '--place',
                        choices=PLACES,
                        required=False,
                        default='Spikersuppa',
                        help='specify place')
    parser.add_argument('-v', '--var',
                        choices=DATA_FIELDS,
                        required=False,
                        default='temperature',
                        help='specify variable')

    return parser.parse_args()


def parse_data(file: TextIOWrapper) -> Generator[EntryObj, None, None]:
    for line in file:
        pline = json.loads(line)
        pline['time'] = dt.datetime.fromisoformat(pline['time'])
        yield pline


def filter_time_range(entries: Iterable[EntryObj],
                      start: dt.time,
                      end: dt.time
                      ) -> Generator[EntryObj, None, None]:
    for entry in entries:
        if start <= entry['time'].time() <= end:
            yield entry


def filter_place(entries: Iterable[EntryObj], place: str
                 ) -> Generator[EntryObj, None, None]:
    for entry in entries:
        for location in entry['location_data']:
            if location['location']['name'] == place:
                yield entry


def extract_entries_field(entries: Iterable[EntryObj], place: str, key: str
                          ) -> Generator[float, None, None]:
    for entry in entries:
        for i in entry['location_data']:
            if i['location']['name'] == place:
                yield i[key]  # type: ignore


def main() -> None:
    args = get_arg_namespace()

    if args.fetch:
        location_data = list(fetch_location_data())
        print(json.dumps(EntryObj(
            location_data=location_data,
            time=str(dt.datetime.now()))))  # type: ignore

        return None

    entries = parse_data(args.file)
    entries = filter_place(entries, args.place)
    entries = filter_time_range(entries, dt.time(args.time[0]), dt.time(args.time[1]))
    ea, eb = itertools.tee(entries)

    pm10 = tuple(extract_entries_field(ea, args.place, 'pm10'))
    cmp = tuple(extract_entries_field(eb, args.place, args.var))

    print(args.place)
    size = len(pm10)
    x = np.arange(size)
    fig, ax = plt.subplots()
    ax.bar(x + 0.2, pm10, width=0.4, color='#55cdfc')
    ax.set_label(args.place)
    ax.legend('pm10', args.var, loc='upper left')
    ax.bar(x - 0.2, cmp, width=0.4, color='#f7a8b8')
    plt.show()

    return None


if __name__ == '__main__':
    main()
