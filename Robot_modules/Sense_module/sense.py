import paho.mqtt.client as mqtt
from Sensors import UltrasonicSensorReader
from collections import deque
from Kobuki import Kobuki


class Body:
    _d_sensors: dict
    _sim_body: Kobuki
    _sensor_reader: UltrasonicSensorReader
    _sensor_queue: deque

    def __init__(self):
        # /dev/ttyUSB0 SENSORS
        # /dev/ttyUSB1 KOBUKI
        self._d_sensors = {}
        self._sim_body = Kobuki()
        self._sensor_reader = UltrasonicSensorReader()
        self._sensor_queue = deque()

        # Inizia il thread per la lettura dei dati di Kobuki
        # self._sim_body.kobukistart(self._sim_body.read_data)

    def sense(self, client):
        # Leggere i dati dei sensori a ultrasuoni, nello specifico recupera l'ultima misurazione
        sensor_data = self._sensor_reader.read_sensor_data()
        if sensor_data:
            self._sensor_queue.append(sensor_data)
        while self._sensor_queue:
            sensor_data = self._sensor_queue.popleft()
            sensor_name = sensor_data['sensor_id']  # Assumendo che sensor_id sia del tipo "S1", "S2", ecc.
            self._d_sensors[sensor_name] = sensor_data['distance']

        # Leggere l'orientazione del robot
        angle = self._sim_body.inertial_sensor_data()['angle']

        # Leggere videocamera
        # Leggere posizione del robot

        # Pubblicare i dati su MQTT
        for name in self._d_sensors.keys():
            client.publish(f"sense/{name}", str(self._d_sensors[name]))
            print(f"Published data from sensor: {name}")
        client.publish(f"sense/orientation", str(angle))


if __name__ == "__main__":

    my_robot = Body()

    client_pub = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_pub.connect("192.168.0.111", 1883)  # IP computer Giovanni

    while True:
        my_robot.sense(client_pub)
