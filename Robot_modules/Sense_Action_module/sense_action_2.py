import time
import threading
import paho.mqtt.client as mqtt
from Sensors import UltrasonicSensorReader
from Sensors import ColorSensorReader
from collections import deque
from Kobuki import Kobuki

BASE_SPEED = 20.0
TURN_SPEED = 15.5


class Body:
    _d_sensors: dict
    _sensor_reader: UltrasonicSensorReader
    _sensor_queue: deque
    _sim_body: Kobuki
    _actuators: list
    _position: dict
    _orientation: str
    _color_reader: ColorSensorReader

    def __init__(self):
        self._d_sensors = {}
        self._sim_body = Kobuki()
        self._sensor_reader = UltrasonicSensorReader()
        self._sensor_queue = deque()
        self.past_action = ""
        self.actual_action = ""
        self._position = {
            "x": 0,
            "y": 0}
        self._orientation = "nord"
        self._color_reader = ColorSensorReader()
        self._rotating = False
        self._active_position = False

    def sense(self, client):
        while True:
            sensor_data = self._sensor_reader.read_sensor_data()
            if sensor_data:
                self._sensor_queue.append(sensor_data)
            while self._sensor_queue:
                sensor_data = self._sensor_queue.popleft()
                sensor_name = sensor_data['sensor_id']  # Assumendo che sensor_id sia del tipo "S1", "S2", ecc.
                self._d_sensors[sensor_name] = sensor_data['distance']

            # Leggere posizione del robot
            self.update_position()

            # Leggere colore
            color = self._color_reader.read_color()
            if color is not None:
                self._d_sensors['color'] = color

            # Pubblicare i dati su MQTT
            for name in self._d_sensors.keys():
                client.publish(f"sense/{name}", str(self._d_sensors[name]))
                print(f"Published data from sensor: {name}")
            client.publish(f"sense/orientation", str(self._orientation))
            client.publish(f"sense/position/x", str(self._position["x"]))
            client.publish(f"sense/position/y", str(self._position["y"]))
            client.publish("sense/rotating", str(self._rotating))
            time.sleep(0.1)

    def move(self, speed, turn):
        self._sim_body.move(speed, speed, turn)

    def go_straight(self):
        self.move(BASE_SPEED, 0)

    def turn_left(self, vel):
        self._rotating = True
        for i in range(45):
            self.move(vel, 1)
        self.update_orientation("left", 1)
        self._rotating = False

    def turn_right(self, vel):
        self._rotating = True
        for i in range(45):
            self.move(vel, -1)
        self.update_orientation("right", 1)
        self._rotating = False

    def go_back(self):
        self._rotating = True
        for i in range(60):
            self.move(TURN_SPEED, -1)
        self.update_orientation("right", 2)
        self._rotating = False

    def exe_action(self, value):
        print("AZIONE IN ESECUZIONE", value)
        if value == "go":
            my_robot.go_straight()
        elif value == "cross" or value == "stop" or value == "Finish":
            print("Stop")
            my_robot.move(0, 0)
        elif value == "turn_left":
            my_robot.turn_left(TURN_SPEED)
        elif value == "turn_right":
            my_robot.turn_right(TURN_SPEED)
        elif value == "go_back":
            my_robot.go_back()

    def update_orientation(self, direction, step):
        if direction == "right" and step == 1:
            if self._orientation == "nord":
                self._orientation = "est"
            elif self._orientation == "est":
                self._orientation = "sud"
            elif self._orientation == "sud":
                self._orientation = "ovest"
            elif self._orientation == "ovest":
                self._orientation = "nord"
            else:
                print("ORIENTATION ERROR")
        elif direction == "right" and step == 2:
            if self._orientation == "nord":
                self._orientation = "sud"
            elif self._orientation == "est":
                self._orientation = "ovest"
            elif self._orientation == "sud":
                self._orientation = "nord"
            elif self._orientation == "ovest":
                self._orientation = "est"
            else:
                print("ORIENTATION ERROR")
        elif direction == "left":
            if self._orientation == "nord":
                self._orientation = "ovest"
            elif self._orientation == "est":
                self._orientation = "nord"
            elif self._orientation == "sud":
                self._orientation = "est"
            elif self._orientation == "ovest":
                self._orientation = "sud"
            else:
                print("ORIENTATION ERROR")

    def update_position(self):
        if self._active_position and not self._rotating:
            if self._orientation == "nord":
                self._position["x"] += 1
            elif self._orientation == "est":
                self._position["y"] += 1
            elif self._orientation == "ovest":
                self._position["y"] -= 1
            elif self._orientation == "sud":
                self._position["x"] -= 1


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(
            f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("controller/#")


def on_message(client, userdata, msg):
    name = msg.topic.split("/")[1]
    value = msg.payload.decode("utf-8")
    my_robot.actual_action = value

    if not my_robot._active_position:
        my_robot._active_position = True
        print("Prima azione ricevuta, _active_position impostato a True.")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        client.subscribe("controls/#")


if __name__ == "__main__":
    my_robot = Body()

    client_pub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True, client_id="pub")
    client_pub.connect("192.168.0.111", 1883)  # IP computer Giovanni

    client_sub = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True, client_id="sub")
    client_sub.connect("192.168.0.111", 1883)
    client_sub.on_connect = on_connect
    client_sub.on_message = on_message
    client_sub.on_subscribe = on_subscribe

    sensing_thread = threading.Thread(target=my_robot.sense, args=(client_pub,))
    sensing_thread.start()

    rotation = False

    while True:
        client_sub.loop()
        print("Rotating", my_robot._rotating)
        if my_robot.actual_action == "go" or my_robot.actual_action == "stop" or my_robot.actual_action == "cross":
            rotation = False
            print("Actual action", my_robot.actual_action)
        elif my_robot.actual_action == "turn_left" or my_robot.actual_action == "turn_right" or my_robot.actual_action == "go_back":
            if not rotation:
                rotation = True
                my_robot.exe_action(my_robot.actual_action)
            else:
                print("Rotazione in corso")
        else:
            print("Error")
