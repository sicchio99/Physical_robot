import paho.mqtt.client as mqtt
from Kobuki import Kobuki

BASE_SPEED = 2.0
ANGLE_TOLERANCE = 0.02
TURN_SPEED = 0.3
SLOW_TURN_SPEED = 0.2
MORE_SLOW_TURN_SPEED = 0.1


class Body:
    _actuators: list
    _sim_body: Kobuki

    def __init__(self, actuators):
        assert isinstance(actuators, list)
        self._actuators = actuators
        self._sim_body = Kobuki()
        # Inizia il thread per la lettura dei dati di Kobuki
        self._sim_body.kobukistart(self._sim_body.read_data)

    def move(self, speed, turn):
        self._sim_body.move(speed, speed, turn)

    def go_straight(self):
        self.move(BASE_SPEED, 0)

    def turn_left(self, vel):
        self.move(vel, -1)

    def turn_right(self, vel):
        self.move(vel, 1)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(
            f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("controller/#")


def on_message(client, userdata, msg):
    name = msg.topic.split("/")[1]
    value = msg.payload.decode("utf-8")
    print(name, value)

    if name == "direction":
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
    elif name == "target":
        if value == "Finish":
            my_robot.move(0, 0)
            client.publish("action", "finish")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        client.subscribe("controls/#")


if __name__ == "__main__":
    my_robot = Body(["leftMotor", "rightMotor"])

    client_mqtt = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("192.168.0.111", 1883)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.loop_forever()
