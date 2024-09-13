import paho.mqtt.client as mqtt
import time
import random
from Crossroad import Crossroad


class Controller:
    _old_action: str
    _free_directions: dict
    _direction: str
    _rotating: bool
    _target_angle: float
    _rotation_sense: str
    _target: bool
    _rotation_done: bool
    _waiting_update_direction: bool
    _update_direction: dict
    _crossroads: list
    _position: dict
    _dx_sx: bool
    _target: bool
    _stop: int

    def __init__(self):
        self._old_action = ""
        self._free_directions = {
            "front": True,
            "left": False,
            "right": False}
        self._direction = "nord"
        self._rotating = False
        self._target_angle = 0.0
        self._rotation_sense = ""
        self._rotation_done = False
        self._waiting_update_direction = False
        self._update_direction = {
            "front": False,
            "left": False,
            "right": False,
            "x": False,
            "y": False
            }
        self._crossroads = []
        self._position = {
            "x": 0.0,
            "y": 0.0}
        self._dx_sx = False
        self._target = False
        self._stop = 0
        self._waiting_rotation = False

    def control_directions(self):
        global client_mqtt
        print("-------INIZIO DEL CONTROLLO----------")
        front = self._free_directions["front"]
        left = self._free_directions["left"]
        right = self._free_directions["right"]
        print("FRONT", front)
        print("LEFT", left)
        print("RIGHT", right)
        print("Update direction", str(self._update_direction))
        print("Waiting update", str(self._waiting_update_direction))

        if self._update_direction["front"] and self._update_direction["left"] and self._update_direction["right"] \
                and self._update_direction["x"] and self._update_direction["y"]:
            self._waiting_update_direction = False

        print("Rotating", self._rotating)
        print("Rotating done", self._rotation_done)

        if not self._rotating:
            if self._rotation_done:
                if front and not left and not right and self._stop != 0:
                    self._stop = 0
                    print("Finish Rotation")
                    self._rotation_done = False
                    return "go"
                else:
                    if self._stop == 0:
                        self._stop = 1
                        return "stop"
                    elif self._stop == 1:
                        time.sleep(5)
                        self._stop = 2
                        print("Rotation done, exit from turn/crossroad")
                        return "go"
                    else:
                        print("Rotation done, exit from turn/crossroad")
                        return "go"
            else:
                print("Old action", self._old_action)
                print("Waiting update", self._waiting_update_direction)
                if self._old_action == "cross" and not self._waiting_update_direction:
                    if (front + left + right) >= 2:
                        if self.is_far_enough(self._position["x"], self._position["y"],
                                              self._crossroads):
                            print("New Cross!")
                            self._crossroads.append(Crossroad(self._position["x"], self._position["y"]))
                            print("Posizone:", self._crossroads[-1].x, self._crossroads[-1].y)
                            print("INCROCI INCONTRATI:")
                            for cross in self._crossroads:
                                print(cross, cross.x, cross.y)
                        else:
                            print("Crossroads already met!")

                        actual_cross = self.find_cross(self._crossroads, self._position)
                        if len(actual_cross.directions) == 0:
                            print("Init directions")
                            actual_cross.initialize_directions(front, left, right, self._direction)
                        else:
                            actual_cross.reverse_direction_status(self._direction)
                        print("Directions status:", str(actual_cross.directions))

                        print("Selection the direction")
                        for el in self._update_direction.keys():
                            self._update_direction[el] = False
                        return self.turn_randomly(actual_cross)
                    else:
                        print("Turn")
                        for el in self._update_direction.keys():
                            self._update_direction[el] = False
                        if left:
                            self._waiting_rotation = True
                            return "turn_left"
                        elif right:
                            self._waiting_rotation = True
                            return "turn_right"

                elif self._old_action == "cross" and self._waiting_update_direction:
                    return "cross"
                else:
                    if front:
                        if not left and not right:
                            return "go"
                        else:
                            print("Crossroad or turn met")
                            client_mqtt.disconnect()
                            time.sleep(9.5)
                            client_mqtt.reconnect()
                            self._waiting_update_direction = True
                            return "cross"
                    else:
                        if not left and not right:
                            print("Blind path")
                            self._waiting_rotation = True
                            return "go_back"
                        else:
                            return "undetermined"
        else:
            print("Rotazione in corso")

    def turn_randomly(self, cross):
        options = cross.get_true_directions()
        print("Available directions: ", str(options))
        choice = random.choice(options)
        print("Direction selected", choice)
        cross.set_direction_status(choice)
        print("New directions status: " + str(cross.directions))

        if choice == self._direction:
            self._rotation_done = True  # usare per far andare dritto il robot
            return "go"
        elif ((self._direction == "nord" and choice == "est") or
              (self._direction == "sud" and choice == "ovest") or
              (self._direction == "est" and choice == "sud") or
              (self._direction == "ovest" and choice == "nord")):
            self._waiting_rotation = True
            return "turn_right"
        elif ((self._direction == "nord" and choice == "ovest") or
              (self._direction == "sud" and choice == "est") or
              (self._direction == "est" and choice == "nord") or
              (self._direction == "ovest" and choice == "sud")):
            self._waiting_rotation = True
            return "turn_left"

    def is_far_enough(self, x, y, crossroads, threshold=0.4):
        for cross in crossroads:
            if abs(cross.x - x) <= threshold and abs(cross.y - y) <= threshold:
                return False
        return True

    def find_cross(self, crossroads_list, coord, threshold=0.4):
        for cross in crossroads_list:
            if abs(cross.x - coord["x"]) <= threshold and abs(cross.y - coord["y"]) <= threshold:
                return cross
        return None

    def update_direction_function(self, name, val):
        if val == "True":
            self._free_directions[name] = True
        else:
            self._free_directions[name] = False
        if self._waiting_update_direction:
            self._update_direction[name] = True

    def update_position(self, name, val):
        self._position[name] = float(val)
        if self._waiting_update_direction:
            self._update_direction[name] = True

    def update_target(self, val):
        if val == "True":
            self._target = True
        else:
            self._target = False

    @property
    def target(self):
        return self._target

    @property
    def rotating(self):
        return self._rotating

    @property
    def rotation_done(self):
        return self._rotation_done

    @property
    def old_action(self):
        return self._old_action

    def update_rotating(self, message_value):
        if message_value == "False":
            if self._rotating:
                self._rotation_done = True
            self._rotating = False
        else:
            self._rotating = True
            self._waiting_rotation = False


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code.is_failure:
        print(
            f"Failed to connect: {reason_code}. loop_forever() will retry connection")
    else:
        client.subscribe("perception/#")


def on_message(client, userdata, msg):
    perception_name = msg.topic.split("/")[1]
    message_value = msg.payload.decode("utf-8")

    print("MESSAGE:", perception_name, message_value)

    match perception_name:
        case "front":
            controller.update_direction_function(perception_name, message_value)
        case "left":
            controller.update_direction_function(perception_name, message_value)
        case "right":
            controller.update_direction_function(perception_name, message_value)
        case "green":
            print("Sensor color:", message_value)
            # controller.update_target(message_value)
        case "orientation":
            controller._direction = message_value
        case "position-x":
            controller.update_position("x", message_value)
        case "position-y":
            controller.update_position("y", message_value)
        case "rotating":
            controller.update_rotating(message_value)

    if not (controller.rotating or controller.rotation_done) and controller.target:
        client.publish("controls/target", "Finish")
        print("FINE")
    else:
        if not controller._waiting_rotation:
            if not controller.rotating:
                control = controller.control_directions()
                print("CONTROL RESULT", control)
                if control != controller.old_action:
                    client.publish(f"controls/direction", control)
                    print("published control:", control)
                    controller._old_action = control
        else:
            print("Attesa inizio rotazione")


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == "__main__":
    controller = (Controller())

    time.sleep(30)

    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.loop_forever()