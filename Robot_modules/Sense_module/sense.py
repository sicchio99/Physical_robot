from SimulatedRobot import SimulatedPioneerBody
import paho.mqtt.client as mqtt
import re


class Body:
    _sensor_array: list
    _d_sensors: dict
    _sim_body: SimulatedPioneerBody

    def __init__(self, sensors):
        assert isinstance(sensors, list)
        self._d_sensors = {}
        for sensor in sensors:
            self._d_sensors[sensor] = 0
        self._sensor_array = list(self._d_sensors.keys())
        self._sim_body = SimulatedPioneerBody("PioneerP3DX")
        self._sim_body.start()

    def sense(self, client):
        vision_values, proximity_values, orientation_value, position_values = self._sim_body.sense()
        for s in self._d_sensors:
            if 'Vision_sensor' in s:
                self._d_sensors[s] = vision_values[0]
            elif 'ultrasonicSensor' in s:
                match = re.search(r'\d+', s)
                if match:
                    index = int(match.group())
                    self._d_sensors[s] = proximity_values[index]
        for name in self._sensor_array:
            client.publish(f"sense/{name}", str(self._d_sensors[name]))
            print(f"Published data from sensor: {name}")
        client.publish(f"sense/orientation", str(orientation_value))
        print(f"Published orientation data")
        client.publish(f"sense/position/x", str(position_values[0]))
        client.publish(f"sense/position/y", str(position_values[1]))
        print(f"Published position data")


if __name__ == "__main__":
    my_robot = Body(["Vision_sensor", "ultrasonicSensor[0]",
                    "ultrasonicSensor[4]", "ultrasonicSensor[7]"])
    print("Keys in _d_sensors:", my_robot._d_sensors.keys())

    client_pub = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_pub.connect("mosquitto", 1883)

    while True:
        my_robot.sense(client_pub)
