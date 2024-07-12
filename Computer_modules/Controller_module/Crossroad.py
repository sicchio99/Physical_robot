import math


class Crossroad:
    x: int
    y: int
    directions: list

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.directions = []

    def initialize_directions(self, front, left, right, orientation):
        actual_dir = self.define_direction(orientation)
        if actual_dir == "nord":
            self.directions.append(["sud", False])
            if front:
                self.directions.append(["nord", True])
            if left:
                self.directions.append(["ovest", True])
            if right:
                self.directions.append(["est", True])
        elif actual_dir == "est":
            self.directions.append(["ovest", False])
            if front:
                self.directions.append(["est", True])
            if left:
                self.directions.append(["nord", True])
            if right:
                self.directions.append(["sud", True])
        elif actual_dir == "ovest":
            self.directions.append(["est", False])
            if front:
                self.directions.append(["ovest", True])
            if left:
                self.directions.append(["sud", True])
            if right:
                self.directions.append(["nord", True])
        elif actual_dir == "sud":
            self.directions.append(["nord", False])
            if front:
                self.directions.append(["sud", True])
            if left:
                self.directions.append(["est", True])
            if right:
                self.directions.append(["ovest", True])

    def define_direction(self, orientation):
        actual_angle = orientation
        current_angle = self.normalize_angle(actual_angle)
        if -0.3 < current_angle < 0.3:
            return "nord"
        elif -1.8 < current_angle < -1.2:
            return "est"
        elif current_angle < -2.8 or current_angle > 2.8:
            return "sud"
        elif 1.2 < current_angle < 1.8:
            return "ovest"

    def get_true_directions(self):
        return [direction[0] for direction in self.directions if direction[1] is True]

    def set_direction_status(self, direction_name):
        for direction in self.directions:
            if direction[0] == direction_name:
                direction[1] = False
                break

        self.reset()

    def reset(self):
        # Controllo se tutte le direzioni sono false
        if all(direction[1] is False for direction in self.directions):
            self.directions[0][1] = True

    def reverse_direction_status(self, direction_name):
        opposite_direction = {
            "nord": "sud",
            "est": "ovest",
            "sud": "nord",
            "ovest": "est"
        }
        if direction_name in opposite_direction:
            opposite_name = opposite_direction[direction_name]
            for direction in self.directions:
                if direction[0] == opposite_name:
                    direction[1] = False
                    break

            self.reset()

    def normalize_angle(self, angle):
        normalized_angle = angle % (2 * math.pi)
        if normalized_angle >= math.pi:
            normalized_angle -= 2 * math.pi
        return normalized_angle
