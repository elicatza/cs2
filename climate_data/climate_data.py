#!/usr/bin/env python3.10

import requests as req
import numpy as np
import numpy.typing as npt
import json
import argparse
import sys
from typing import TypedDict
import datetime as dt
# import dateutil


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
    pm10: float  # 0 - 600 μg/m3


class BigData(TypedDict):
    time: str
    location_data: list[LocationData]


HEADERS = {
    'Content-type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'User-Agent': 'Python/3.10.9'
}

# Data: https://api.nilu.no/aq/utd?areas=oslo&components=pm10
# About data: https://en.wikipedia.org/wiki/Air_quality_index#Computing_the_AQI
# get data Three times a day
# Get relevant data
# Temperatur sammenlignet med CO_2 utslitt
# Daemon
# Make grafs
# Make statistics

# Relevant nila data: place(lat, long), time, weather (rain, wind), pressure,
# ME: create a map, with color over time

# Fetch data: 30 min


def fetch_location_data() -> list[LocationData]:
    # API docs: https://api.nilu.no/
    nilu_url = "https://api.nilu.no/aq/utd?areas=oslo&components=pm10"
    nilu_res = req.get(nilu_url, headers=HEADERS)

    if nilu_res.status_code != 200:
        print(f"ERROR: invalid status code from `{nilu_url}`")
        exit(1)

    nilu_data = json.loads(nilu_res.text)
    places: list[LocationData] = list()
    for place in nilu_data:

        # Get weather for location
        # API docs: https://api.met.no/weatherapi/locationforecast/2.0/documentation
        met_url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}"
        met_url = met_url.format(place['latitude'], place['longitude'])
        met_res = req.get(met_url, headers=HEADERS)

        if met_res.status_code != 200:
            print(f"ERROR: invalid status code from `{met_url}`")
            exit(1)

        met_data = json.loads(met_res.text)
        met_pdata = met_data['properties']['timeseries'][0]['data']['instant']['details']
        places.append(
                LocationData(
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
        )

    return places


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare nilu and metrologisk_institutt data',
                                     prefix_chars='--',
                                     allow_abbrev=True)
    parser.add_argument('-f',
                        '--fetch',
                        action='store_true',
                        help='fetch data and write to file')
    # Parse args if in fetch data mode or analyze data (default)
    # if fetch: get relevant data and write to file
    # if not fetch : show data to user. map, graphs
    # plotly, geopanda, osmnx (folium)
    args = parser.parse_args()

    if args.fetch:
        location_data = fetch_location_data()
    else:
        print("ERROR: not supported yet use --fetch")
        exit(1)

    data_obj = BigData(location_data=location_data, time=str(dt.datetime.now()))

    print(json.dumps(data_obj))


if __name__ == '__main__':
    main()
