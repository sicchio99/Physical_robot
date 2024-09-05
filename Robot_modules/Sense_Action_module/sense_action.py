import time
import threading
import paho.mqtt.client as mqtt
from Sensors import UltrasonicSensorReader
from Sensors import ColorSensorReader
from collections import deque
from Kobuki import Kobuki
import imageio

BASE_SPEED = 20.0
TURN_SPEED = 40.0
SLOW_TURN_SPEED = 20.0
MORE_SLOW_TURN_SPEED = 10.0


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

    def sense(self, client):
        while True:
            sensor_data = self._sensor_reader.read_sensor_data()
            if sensor_data:
                self._sensor_queue.append(sensor_data)
            while self._sensor_queue:
                sensor_data = self._sensor_queue.popleft()
                sensor_name = sensor_data['sensor_id']  # Assumendo che sensor_id sia del tipo "S1", "S2", ecc.
                self._d_sensors[sensor_name] = sensor_data['distance']

            # Leggere l'orientazione del robot
            angle = self._sim_body.inertial_sensor_data()['angle']

            # Leggere posizione del robot
            self._orientation = self.define_direction(angle[1])
            self.update_position()

            # Leggere colore
            color = self._color_reader.read_color()
            if color is not None:
                self._d_sensors['color'] = color

            # Pubblicare i dati su MQTT
            for name in self._d_sensors.keys():
                client.publish(f"sense/{name}", str(self._d_sensors[name]))
                print(f"Published data from sensor: {name}")
            client.publish(f"sense/orientation", str(angle))
            client.publish(f"sense/position/x", str(self._position["x"]))
            client.publish(f"sense/position/y", str(self._position["y"]))
            time.sleep(0.1)

    def convert_byte_to_angle(self, byte_value):
        print("byte value", byte_value)
        # Convert the byte value (0-255) to degrees (0-360)
        if byte_value <= 70:
            # Scaling 0-70 to 0-180 degrees
            degrees = (byte_value / 70) * 180
        else:
            # Scaling 185-255 to 180-360 degrees
            degrees = 180 + ((byte_value - 185) / 70) * 180
            # Scalare 71-255 a 180-360 gradi VERSIONE CHAT GPT
            # degrees = 180 + ((byte_value - 71) / 184) * 180

        print("Angolo in gradi", degrees)
        return degrees

    def move(self, speed, turn):
        self._sim_body.move(speed, speed, turn)

    def go_straight(self):
        self.move(BASE_SPEED, 0)

    def turn_left(self, vel):
        self.move(vel, 1)

    def turn_right(self, vel):
        self.move(vel, -1)

    def exe_action(self, value):
        print("AZIONE IN ESECUZIONE", value)
        if value == "go":
            my_robot.go_straight()
        elif value == "cross":
            print("Stop")
            my_robot.move(0, 0)
        elif value == "turn_left":
            my_robot.turn_left(TURN_SPEED)
        elif value == "turn_left_slow":
            my_robot.turn_left(SLOW_TURN_SPEED)
        elif value == "turn_left_more_slow":
            my_robot.turn_left(MORE_SLOW_TURN_SPEED)
        elif value == "turn_right":
            my_robot.turn_right(TURN_SPEED)
        elif value == "turn_right_slow":
            my_robot.turn_right(SLOW_TURN_SPEED)
        elif value == "turn_right_more_slow":
            my_robot.turn_right(MORE_SLOW_TURN_SPEED)

    def define_direction(self, orientation):
        degrees = self.convert_byte_to_angle(orientation)
        if degrees < 20.0 or degrees > 340.0:
            return "nord"
        elif 70.0 < degrees < 110.0:
            return "est"
        elif 160.0 < degrees < 200.0:
            return "sud"
        elif 250.0 < degrees < 290.0:
            return "ovest"

    def update_position(self):
        if self._orientation == "nord":
            self._position["x"] += 1
        elif self._orientation == "est":
            self._position["y"] += 1
        elif self._orientation == "ovest":
            self._position["y"] -= 1
        elif self._orientation == "sud":
            self._position["x"] -= 1

    """
    def get_frame(self):
        ret, frame = self._cap.read()

        if not ret:
            print("Errore nel ricevere frame dalla webcam")
            return None

        return frame
    """


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

    while True:
        client_sub.loop()
        if my_robot._sim_body.is_moving:
            print("Robot is already moving")
            pass
        else:
            my_robot.exe_action(my_robot.actual_action)
