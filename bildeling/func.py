#!/usr/bin/env python3


import enum
import datetime as dt
from dataclasses import dataclass
from types import SimpleNamespace


class FuelType(enum.Enum):
    DISEL = enum.auto()
    OIL = enum.auto()
    EL = enum.auto()


@dataclass
class Car:
    c_type: str
    id: str
    km: int
    available: int = 0


@dataclass
class StorageCar(Car):
    def __init__(self, c_type: str, id: str, km: int, size_m3: int, mass: int):
        super().__init__(c_type, id, km)
        self.size_m3 = size_m3
        self.mass = mass

        if self.mass > 3500:
            self.asphalt = True
        else:
            self.asphalt = False


class Member:

    def __init__(self, name: str, uid: str, member: dt.timedelta):
        self.name = name
        self.uid = uid
        self.member = member
        self.renting: list[Car] = []


class Rent:
    def __init__(self, car: Car, member: Member):
        self.car = car
        self.member = member

    def rent(self) -> bool:
        if self.car.available:
            self.car.available = False
            self.member.renting.append(self.car)
            return True
        return False

    def deliver(self, dist: int) -> None:
        self.car.km += dist
        self.car.available = True
        # self.member.renting.remove(self.car)
        return None


def main() -> None:
    model_t = Car("Fort model T", "rTiIGw74", 70_000)
    john = Member("John", "6ZOYpG1q", dt.timedelta(days=20))
    r_instance = Rent(model_t, john)
    r_instance.rent()
    print(john.renting)
    r_instance.deliver(300)
    print(john.renting)
    print(model_t.km)
    return None


if __name__ == '__main__':
    main()
