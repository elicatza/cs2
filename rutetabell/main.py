#!/usr/bin/env python3
import datetime
import copy
import json


COLUMNS_PER_ROW = 10


def main():

    fp = open("./rutetabell.json")
    routes = json.load(fp)

    for stop in routes:
        print(f'\n\n{stop["name"]}', end="")

        end_day = 0 if stop["start_hour"] < stop["end_hour"] else 1

        first_time = datetime.timedelta(hours=stop["start_hour"], minutes=stop["start_minute"])
        last_time = datetime.timedelta(days=end_day, hours=stop["end_hour"], minutes=stop["end_minute"])
        intervall = datetime.timedelta(minutes=stop["intervall"])

        cur_time = copy.deepcopy(first_time)

        i = 0
        while cur_time < last_time:
            if i % COLUMNS_PER_ROW == 0:
                print("")
            cur_time += intervall
            print(f"{cur_time.seconds // (60 ** 2):>2}:{(cur_time.seconds // 60) % 60:02}", end=" | ")
            i += 1

    fp.close()


if __name__ == "__main__":
    main()
