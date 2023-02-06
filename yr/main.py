#!/usr/bin/env python

import requests as req
import numpy as np
import numpy.typing as npt
import json
import argparse
import sys

HEADERS = {
    'Content-type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'User-Agent': 'Python/3.10.9'
}

DEFAULT_LAT = 59.9079
DEFAULT_LON = 10.7862


def parse_city_data() -> npt.NDArray[np.generic]:
    dt = np.dtype([('place', 'U32'), ('lat', 'f4'), ('long', 'f4')])
    return np.loadtxt('./place_data.txt', dtype=dt)


def main() -> None:
    parser = argparse.ArgumentParser(description='Get temperature',
                                     prefix_chars='--',
                                     allow_abbrev=True)
    parser.add_argument('-l',
                        '--list',
                        action='store_true',
                        help='Lists all cities in Norway')
    parser.add_argument('-s',
                        '--select',
                        metavar='CITY',
                        type=str,
                        help='select city')

    args = parser.parse_args()
    lat = DEFAULT_LAT
    lon = DEFAULT_LON

    if args.list:
        cities = parse_city_data()
        print(cities['place'])
        return None

    if args.select:
        cities = parse_city_data()
        if args.select in cities['place']:
            id = np.where(cities['place'] == args.select)[0][0]
            lat = cities['lat'][id]
            lon = cities['long'][id]
        else:
            print("ERROR: city not in list")
            print(f"You can check available cities with `{sys.argv[0]} -l`")
            exit(1)

    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}".format(lat, lon)
    res = req.get(url, headers=HEADERS)

    if res.status_code == 200:
        json_obj = json.loads(res.text)

        temp = json_obj['properties']['timeseries'][0]['data']['instant'][
            'details']['air_temperature']
        print(temp)
    else:
        print("ERORR: invalid response")
        exit(1)


if __name__ == '__main__':
    main()
