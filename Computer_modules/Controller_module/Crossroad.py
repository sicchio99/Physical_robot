class Crossroad:
    x: int
    y: int
    directions: list

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.directions = []

    def initialize_directions(self, front, left, right, direction):
        if direction == "nord":
            self.directions.append(["sud", False])
            if front:
                self.directions.append(["nord", True])
            if left:
                self.directions.append(["ovest", True])
            if right:
                self.directions.append(["est", True])
        elif direction == "est":
            self.directions.append(["ovest", False])
            if front:
                self.directions.append(["est", True])
            if left:
                self.directions.append(["nord", True])
            if right:
                self.directions.append(["sud", True])
        elif direction == "ovest":
            self.directions.append(["est", False])
            if front:
                self.directions.append(["ovest", True])
            if left:
                self.directions.append(["sud", True])
            if right:
                self.directions.append(["nord", True])
        elif direction == "sud":
            self.directions.append(["nord", False])
            if front:
                self.directions.append(["sud", True])
            if left:
                self.directions.append(["est", True])
            if right:
                self.directions.append(["ovest", True])

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
