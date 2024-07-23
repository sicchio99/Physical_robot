import paho.mqtt.client as mqtt
import array
import numpy as np
import cv2
import json

MIN_DISTANCE = 20


class Perceptor:
    # CAPIRE A QUALI SENSORI CORRISPONDONO S1, S2, S3 (FRONTALE, DX, SX)
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

    def get_image_from_sensor(self, image, resolution):
        if image is not None and resolution is not None:
            img_array = array.array('B', image)
            img_np = np.array(img_array, dtype=np.uint8)
            img_np = img_np.reshape((resolution[1], resolution[0], 3))
            return img_np
        else:
            print(f"Failed to capture image from vision sensor.")
            return None

    def detect_green_object(self, image):
        # Convert the image to HSV
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Define the range for green color in HSV
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])
        # Threshold the image to get only green colors
        mask = cv2.inRange(hsv_image, lower_green, upper_green)
        # Find contours in the masked image
        contours, _ = cv2.findContours(
            mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return len(contours) > 0

    def percept(self, values):
        print("Arrivo:", values)
        for key, value in values.items():
            print("key", key, "value", value)
            if key == "S1":
                self._perception["front"] = self.is_free(value)
                print("Left", self.is_free(value))
            elif key == "S2":
                self._perception["left"] = self.is_free(value)
                print("Front", self.is_free(value))
            elif key == "S3":
                self._perception["right"] = self.is_free(value)
                print("Right", self.is_free(value))
            #elif key == "Vision_sensor":
                #sensor_value = eval(value)
                #image = sensor_value[0]
                #resolution = sensor_value[1]
                #img = self.get_image_from_sensor(image, resolution)
                #if img is not None and self.detect_green_object(img):
                    #print("Green object detected. Stopping the simulation.")
                    #self._perception["green"] = True
                #else:
                    #print("No green")
                    #self._perception["green"] = False
            elif key == "orientation":
                print("Orientation", str(value))
                if value:
                    value_list = json.loads(value)
                    angle = self.convert_byte_to_angle(value_list[1])
                    self._perception["orientation"] = angle
            #elif key == "position-x":
                #print("Position x", str(value))
                #self._perception["position_x"] = value
            #elif key == "position-y":
                #print("Position y", str(value))
                #self._perception["position_y"] = value

    def convert_byte_to_angle(self, byte_value):
        print("byte value", byte_value)
        # Convert the byte value (0-255) to degrees (0-360)
        if byte_value <= 70:
            # Scaling 0-70 to 0-180 degrees
            degrees = (byte_value / 70) * 180
        else:
            # QUESTA VERSIONE FUNZIONAVA MA SECONDO CHATGPT NON E' CORRETTA
            # SE NON FUNZIONA BENE USARE QUELLA SOTTO COMMENTATA
            # Scaling 185-255 to 180-360 degrees
            degrees = 180 + ((byte_value - 185) / 70) * 180

            # Scalare 71-255 a 180-360 gradi VERSIONE CHAT GPT
            # degrees = 180 + ((byte_value - 71) / 184) * 180

        print("Angolo in gradi", degrees)
        return degrees

    @property
    def sensor_values(self):
        return self._sensor_values

    @property
    def perception(self):
        return self._perception


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
    if sensor_name[1] == "position":
        perceptor.sensor_values[f"position-{sensor_name[2]}"] = message_value
    else:
        if sensor_name[1].endswith("S1"):
            sensor_name[1] = "S1"
        perceptor.sensor_values[sensor_name[1]] = message_value

    perceptor.percept(perceptor.sensor_values)

    for key, value in perceptor.perception.items():
        client.publish(f"perception/{key}", str(value))
        print("Published on", key, "with value", value)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0].is_failure:
        print(f"Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"Broker granted the following QoS: {reason_code_list[0].value}")


if __name__ == "__main__":
    perceptor = Perceptor(sensors=["S1", "S2",
                                   "S3"])
    client_mqtt = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, reconnect_on_failure=True)
    client_mqtt.connect("192.168.0.111", 1883)  # IP computer Giovanni
    client_mqtt.on_connect = on_connect
    client_mqtt.on_message = on_message
    client_mqtt.on_subscribe = on_subscribe
    client_mqtt.loop_forever()
