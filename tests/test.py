import time as t
from tests.Kobuki import Kobuki
import numpy as np


def start():
    i = 0

    while (i < 10):
        t.sleep(1)
        i = i + 1
        # kobuki.move(40, 40, 0)  # 50, 50, 0: 0.045s
        kobuki.move(40, 20, 1)
        gyro_data = kobuki.gyro_velocity_data()
        print("Gyro:", gyro_data)
        # 100, 100, 0: 0.084s
        # 50, 0, 1: 18s per la rotazione oraria
        # 8s per fermarsi
        # Dati di velocità angolare
        x_velocity = gyro_data['angular velocity of x: ']
        y_velocity = gyro_data['angular velocity of y: ']
        z_velocity = gyro_data['angular velocity of z: ']

        # Integrazione numerica per ottenere l'orientazione
        dt = 0.1  # intervallo di tempo (esempio, in secondi)
        orientation_x = np.cumsum(x_velocity) * dt
        orientation_y = np.cumsum(y_velocity) * dt
        orientation_z = np.cumsum(z_velocity) * dt

        # L'orientazione totale può essere rappresentata come un vettore di orientazione
        orientation = np.array([orientation_x[-1], orientation_y[-1], orientation_z[-1]])

        # Stampa dell'orientazione in radianti
        print("Orientazione in radianti:", orientation)
    if (i < 10):
        kobuki.move(0, 0, 0)  # 2s di ritardo nel fermarsi


if __name__ == "__main__":
    kobuki = Kobuki()
    kobuki.kobukistart(start)
