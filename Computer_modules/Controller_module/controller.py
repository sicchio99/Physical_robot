import paho.mqtt.client as mqtt
import time
import random
from Crossroad import Crossroad

MAX_CORRECTION = 50
ANGLE_TOLERANCE = 20.0


class Controller:
    _old_action: str
    _free_directions: dict
    _direction: float
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

    def __init__(self):
        self._old_action = ""
        self._free_directions = {
            "front": True,
            "left": False,
            "right": False}
        self._direction = 0.0
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
        # if self._update_direction["front"] and self._update_direction["left"] and self._update_direction["right"]:
            self._waiting_update_direction = False

        print("Rotating", self._rotating)
        print("Rotating done", self._rotation_done)

        if not self._rotating:
            if self._rotation_done:
                if front and not left and not right:
                    print("Finish Rotation")
                    self._rotation_done = False
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
                        actual_dir = actual_cross.define_direction(controller._direction)
                        if len(actual_cross.directions) == 0:
                            print("Init directions")
                            actual_cross.initialize_directions(front, left, right, self._direction)
                        else:
                            actual_cross.reverse_direction_status(actual_dir)
                        print("Directions status:", str(actual_cross.directions))

                        print("Selection the direction")
                        self._rotating = True
                        for el in self._update_direction.keys():
                            self._update_direction[el] = False
                        return self.turn_randomly(actual_cross, actual_dir)
                    else:
                        print("Turn")
                        self._rotating = True
                        for el in self._update_direction.keys():
                            self._update_direction[el] = False
                        if left:
                            return self.turn_left()
                        elif right:
                            return self.turn_right()

                elif self._old_action == "cross" and self._waiting_update_direction:
                    return "cross"
                else:
                    if front:
                        if not left and not right:
                            return "go"
                        else:
                            print("Crossroad or turn met")
                            client_mqtt.disconnect()
                            print("Inizio Sleep")
                            time.sleep(9)
                            print("Fine Sleep")
                            client_mqtt.reconnect()
                            self._waiting_update_direction = True
                            return "cross"
                    else:
                        if not left and not right:
                            print("Blind path")
                            self._rotating = True
                            return self.go_back()
                        else:
                            return "undetermined"
        else:
            return self.set_robot_orientation(self._target_angle, self._rotation_sense, self._dx_sx)

    def go_back(self):
        current_angle = self._direction
        self._dx_sx = False
        if current_angle < 20.0 or current_angle > 340.0:
            self._target_angle = 180.0
        elif 70.0 < current_angle < 110.0:
            self._target_angle = 270.0
            self._dx_sx = True
        elif 160.0 < current_angle < 200.0:
            self._target_angle = 360.0
        elif 250.0 < current_angle < 290.0:
            self._target_angle = 90.0
            self._dx_sx = True
        self._rotation_sense = "front"
        return self.set_robot_orientation(self._target_angle, self._rotation_sense, self._dx_sx)

    def set_robot_orientation(self, target_angle, dir, dx_sx):
        current_angle = self._direction
        print("CURRENT ROTATION ANGLE", current_angle)
        if dir == "front" and dx_sx:
            diff = abs(target_angle - current_angle)
        else:
            diff = abs(abs(target_angle) - abs(current_angle))
        print("Difference", diff)
        if diff > ANGLE_TOLERANCE:
            if dir == 'right' or dir == 'front':
                if diff > 45.0:
                    return "turn_right"
                elif 30.0 < diff < 45.0:
                    return "turn_right_slow"
                else:
                    return "turn_right_more_slow"
            elif dir == 'left':
                if diff > 45.0:
                    return "turn_left"
                elif 30.0 < diff < 45.0:
                    return "turn_left_slow"
                else:
                    return "turn_left_more_slow"
        else:
            self._rotating = False
            self._rotation_done = True
            self._dx_sx = False
            return "go"

    def turn_right(self):
        self.find_target_angle("right")
        self._rotation_sense = "right"
        return self.set_robot_orientation(self._target_angle, self._rotation_sense, self._dx_sx)

    def turn_left(self):
        self.find_target_angle("left")
        self._rotation_sense = "left"
        return self.set_robot_orientation(self._target_angle, self._rotation_sense, self._dx_sx)

    def turn_randomly(self, cross, actual_dir):
        options = cross.get_true_directions()
        print("Available directions: ", str(options))
        choice = random.choice(options)
        print("Direction selected", choice)
        cross.set_direction_status(choice)
        print("New directions status: " + str(cross.directions))

        if choice == actual_dir:
            self._rotating = False
            self._rotation_done = True  # usare per far andare dritto il robot
            return "go"
        elif ((actual_dir == "nord" and choice == "est") or
              (actual_dir == "sud" and choice == "ovest") or
              (actual_dir == "est" and choice == "sud") or
              (actual_dir == "ovest" and choice == "nord")):
            return self.turn_right()
        elif ((actual_dir == "nord" and choice == "ovest") or
              (actual_dir == "sud" and choice == "est") or
              (actual_dir == "est" and choice == "nord") or
              (actual_dir == "ovest" and choice == "sud")):
            return self.turn_left()

    def find_target_angle(self, direction):
        current_angle = self._direction
        print("Current angle", current_angle)
        if direction == 'right':
            if current_angle < 20.0 or current_angle > 340.0:
                self._target_angle = 270.0
            elif 70.0 < current_angle < 110.0:
                self._target_angle = 0.0
            elif 160.0 < current_angle < 200.0:
                self._target_angle = 90.0
            elif 250.0 < current_angle < 290.0:
                self._target_angle = 180.0
        if direction == 'left':
            if current_angle < 20.0 or current_angle > 340.0:
                self._target_angle = 90.0
            elif 70.0 < current_angle < 110.0:
                self._target_angle = 180.0
            elif 160.0 < current_angle < 200.0:
                self._target_angle = 270.0
            elif 250.0 < current_angle < 290.0:
                self._target_angle = 0.0
        print("Target angle calcolato", self._target_angle)

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
            print("VEDRE IN CAMERA:",message_value)
            # controller.update_target(message_value)
        case "orientation":
            controller._direction = float(message_value)
        case "position-x":
            controller.update_position("x", message_value)
        case "position-y":
            controller.update_position("y", message_value)

    if not (controller.rotating or controller.rotation_done) and controller.target:
        client.publish("controls/target", "Finish")
        print("FINE")
    else:
        control = controller.control_directions()
        print("CONTROL RESULT", control)
        if control != controller.old_action:
            client.publish(f"controls/direction", control)
            print("published control:", control)
            controller._old_action = control
        #client.publish(f"controls/direction", control)
        #print("published control:", control)
        #controller._old_action = control


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == "__main__":
    controller = (Controller())

    time.sleep(15)

    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("mosquitto", 1883)
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.loop_forever()
