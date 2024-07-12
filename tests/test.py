import time as t
from tests.Kobuki import Kobuki
import numpy as np
import math


def convert_byte_to_angle(byte_value):
    print("byte value", byte_value)
    # Convert the byte value (0-255) to degrees (0-360)
    if byte_value <= 70:
        # Scaling 0-70 to 0-180 degrees
        degrees = (byte_value / 70) * 180
    else:
        # Scaling 185-255 to 180-360 degrees
        degrees = 180 + ((byte_value - 185) / 70) * 180
    print("Angolo in gradi", degrees)
    # return degrees * (math.pi / 180)
    return degrees


def start():
    i = 0
    print("start")
    angle = []
    # while i < 10:
    while True:
        # t.sleep(1)
        # i = i + 1
        # kobuki.move(40, 40, 0)  # 50, 50, 0: 0.045s
        # print("move", i)
        if len(angle) > 0:
            kobuki.move(20, 20, 1)
            angle = kobuki.inertial_sensor_data()['angle']
            print("Angle", angle)
            radius = convert_byte_to_angle(angle[1])
            # print("Actual angle", radius)
            if 90 < radius < 100:
                kobuki.move(0, 0, 0)
                break

        else:
            print("Data not ready")
            angle = kobuki.inertial_sensor_data()['angle']
            print("Angle", angle)

    kobuki.move(0,0,0)
    # if i < 10:
        # kobuki.move(0, 0, 0)  # 2s di ritardo nel fermarsi


if __name__ == "__main__":
    kobuki = Kobuki()
    kobuki.kobukistart(start)
