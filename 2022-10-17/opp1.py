#!/usr/bin/env python3
WASTE_BENSIN = 2.32
WASTE_DISEL = 2.66


# Type check for 1 or 2
def two_option(var):
    if var != '1' and var != '2':
        return False
    else:
        return var


def main():
    liter_per_km = friendly_input("Enter liters fuel per kilomiter: ",
                                  float,
                                  "Invalid input. has to be a number!")

    km_in_year = friendly_input("Enter how many kilometers you drive per year: ",
                                float,
                                "Invalid input. has to be a number!")

    fuel_type = friendly_input("[1] Bensin\n[2] Disel\nEnter number of corresponding fuel type: ",
                               two_option,
                               "Invalid input. has to be a number!")

    if fuel_type == "1":
        co2 = liter_per_km * WASTE_BENSIN
    elif fuel_type == "2":
        co2 = liter_per_km * WASTE_DISEL

    print(f"You produce {co2:.1f}kg CO2 per mile")
    print(f"You produce {co2 * km_in_year:.1f}kg CO2 each year")


# Type check function can be builtin python, or function returning var / False,
# depending on if condition is met
def friendly_input(prompt, type_check, invalid_message):
    while True:
        try:
            user_input = type_check(input(prompt))
            if user_input is False:
                raise ValueError
            break
        except (EOFError, KeyboardInterrupt):
            exit(0)
        except ValueError:
            print(invalid_message)

    return user_input


if __name__ == "__main__":
    main()
