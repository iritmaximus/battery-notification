#!/usr/bin/env python3.10
# Gentoo wiki told me this: https://wiki.gentoo.org/wiki/Python

import subprocess
from time import sleep

BAT_PATH = "/sys/class/power_supply/BAT0"
UPDATE_INTERVAL = 15  # seconds


def main():
    bat_full_path = BAT_PATH + "/energy_full"
    bat_now_path = BAT_PATH + "/energy_now"
    bat_status_path = BAT_PATH + "/status"

    bat_charges = {50: False, 30: False, 20: False, 10: False, 5: False}

    while True:
        try:
            bat_full = int(read_file(bat_full_path))
        except LookupError as e:
            print(e)
            bat_full = -1
        except ValueError:
            print("Value cannot be casted to an int")
            bat_full = -1

        try:
            bat_now = int(read_file(bat_now_path))
        except LookupError as e:
            print(e)
            bat_now = -1
        except ValueError as e:
            print("Value cannot be casted to an int")
            bat_now = -1

        try:
            bat_status = read_file(bat_status_path)
        except LookupError as e:
            print(e)
            bat_status = "?"

        bat_percentage = calculate_bat_percentage(bat_now, bat_full)
        print(bat_percentage, bat_status)

        if (
            not check_if_notified(bat_percentage, bat_charges)[0]
            and bat_status != "Charging"
        ):
            send_battery_notification(bat_percentage)

        sleep(UPDATE_INTERVAL)


def check_if_notified(bat_percentage: int, bat_charges: dict):
    last_threshold_crossed = -1
    for index, item in enumerate(bat_charges):
        if bat_percentage < item:
            if index > 0:
                last_threshold_crossed = list(bat_charges.keys())[index - 1]
            else:
                last_threshold_crossed = list(bat_charges.keys())[index]
            break

    print("Last threshold crossed: ", last_threshold_crossed)
    if last_threshold_crossed != -1 and not bat_charges.get(last_threshold_crossed):
        bat_charges[last_threshold_crossed] = True
        return (False, last_threshold_crossed)
    else:
        return (True, last_threshold_crossed)


def calculate_bat_percentage(bat_now: int, bat_full: int) -> int:
    return round((bat_now / bat_full) * 100)


def read_file(filepath: str) -> str | None:
    file_data = ""
    with open(filepath, "r") as f:
        for line in f:
            file_data = line.strip()

    if file_data != "":
        return file_data

    raise LookupError(f"No data found in {filepath}")


def send_battery_notification(charge_left: int):
    cmd = f'notify-send "Battery: " -h int:value:{charge_left} -h string:synchronous:volume'
    # cmd = f'dunstify "Battery: " -h int:value:{charge_left}'
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":
    main()
