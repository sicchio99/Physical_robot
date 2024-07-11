import time as t
from tests.Kobuki import Kobuki


def start():
    i = 0

    while (i < 10):
        t.sleep(1)
        i = i + 1
        kobuki.move(40, 40, 0)  # 50, 50, 0: 0.045s
        # 100, 100, 0: 0.084s
        # 50, 0, 1: 18s per la rotazione oraria
        # 8s per fermarsi
    if (i < 10):
        kobuki.move(0, 0, 0)  # 2s di ritardo nel fermarsi


if __name__ == "__main__":
    kobuki = Kobuki()
    kobuki.kobukistart(start)
