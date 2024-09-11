import paho.mqtt.client as mqtt

MIN_DISTANCE = 25


class Perceptor:
    _my_sensors: list
    _sensor_values: dict
    _perception: dict

    def __init__(self, sensors):
        self._my_sensors = sensors
        self._perception = {}
        self._sensor_values = {}
        for s in sensors:
            self._sensor_values[s] = 0

    def is_free(self, dist):
        return float(dist) == 0 or float(dist) > MIN_DISTANCE

    def percept(self, key, key2):
        if key == "S1":
            self._perception["front"] = self.is_free(self._sensor_values[key])
            print("Front", self.is_free(self._sensor_values[key]))
        elif key == "S2":
            self._perception["right"] = self.is_free(self._sensor_values[key])
            print("Right", self.is_free(self._sensor_values[key]))
        elif key == "S3":
            self._perception["left"] = self.is_free(self._sensor_values[key])
            print("Left", self.is_free(self._sensor_values[key]))
        elif key == "orientation":
            print("Orientation", str(self._sensor_values[key]))
            self._perception["orientation"] = self._sensor_values[key]
        elif key == "position":
            if key2 == "x":
                self._perception["position-x"] = self._sensor_values["position-x"]
            elif key2 == "y":
                self._perception["position-y"] = self._sensor_values["position-y"]
        elif key == "rotating":
            print("Rotating", str(self._sensor_values[key]))
            self._perception["rotating"] = self._sensor_values[key]

    @property
    def sensor_values(self):
        return self._sensor_values

    @property
    def perception(self):
        return self._perception

    def find_name(self, value, value2):
        if value == "S1":
            return "front"
        elif value == "S2":
            return "right"
        elif value == "S3":
            return "left"
        elif value == "orientation":
            return value
        elif value == "position" and value2 == "x":
            return "position-x"
        elif value == "position" and value2 == "y":
            return "position-y"


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(
            f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("sense/#")


def on_message(client, userdata, msg):
    sensor_name = msg.topic.split("/")
    message_value = msg.payload.decode("utf-8")
    print("Received")
    if sensor_name[1] != 'color':
        if sensor_name[1] == "position":
            perceptor.sensor_values[f"position-{sensor_name[2]}"] = message_value
        else:
            if sensor_name[1].endswith("S1"):
                sensor_name[1] = "S1"
            perceptor.sensor_values[sensor_name[1]] = message_value

        if len(sensor_name) > 2:
            perceptor.percept(sensor_name[1], sensor_name[2])
            name = perceptor.find_name(sensor_name[1], sensor_name[2])
        else:
            perceptor.percept(sensor_name[1], "")
            name = perceptor.find_name(sensor_name[1], "")
        client.publish(f"perception/{name}", str(perceptor.perception[name]))
        print("Published on", name, "with value", perceptor.perception[name])
    else:
        if message_value == "Verde":
            client.publish("perception/green", "True")
        else:
            client.publish("perception/green", "False")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == "__main__":
    perceptor = Perceptor(sensors=["S1", "S2",
                                   "S3"])
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)  # IP computer Giovanni
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.loop_forever()