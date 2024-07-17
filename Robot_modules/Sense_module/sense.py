import paho.mqtt.client as mqtt
from Sensors import UltrasonicSensorReader
from collections import deque
from Kobuki import Kobuki


class Body:
    _sensor_array: list
    _d_sensors: dict
    # _sim_body: Kobuki
    _sensor_reader: UltrasonicSensorReader
    _sensor_queue: deque

    def __init__(self, sensors):
        assert isinstance(sensors, list)
        self._d_sensors = {}
        for sensor in sensors:
            self._d_sensors[sensor] = 0
        self._sensor_array = list(self._d_sensors.keys())
        # self._sim_body = Kobuki()
        self._sensor_reader = UltrasonicSensorReader()
        self._sensor_queue = deque()

        # Inizia il thread per la lettura dei dati di Kobuki
        # self._sim_body.kobukistart(self._sim_body.read_data)

    def sense(self, client):
        # Leggere i dati dei sensori a ultrasuoni
        sensor_data = self._sensor_reader.read_sensor_data()
        if sensor_data:
            self._sensor_queue.append(sensor_data)
        while self._sensor_queue:
            sensor_data = self._sensor_queue.popleft()
            sensor_name = f"ultrasonicSensor[{sensor_data['sensor_id'][1:]}]"  # Assumendo che sensor_id sia del tipo "S1", "S2", ecc.
            self._d_sensors[sensor_name] = sensor_data['distance']

        # Leggere l'orientazione del robot
        # angle = self._sim_body.inertial_sensor_data()['angle']

        # Leggere videocamera
        # Leggere posizione del robot

        # Pubblicare i dati su MQTT
        for name in self._sensor_array:
            client.publish(f"sense/{name}", str(self._d_sensors[name]))
            print(f"Published data from sensor: {name}")
        # client.publish(f"sense/orientation", str(angle))


if __name__ == "__main__":
    my_robot = Body(["Vision_sensor", "ultrasonicSensor[0]",
                    "ultrasonicSensor[4]", "ultrasonicSensor[7]"])
    # print("Keys in _d_sensors:", my_robot._d_sensors.keys())

    client_pub = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_pub.connect("192.168.0.111", 1883)

    while True:
        my_robot.sense(client_pub)
