import base64
import paho.mqtt.client as mqtt
import numpy as np
import json
from PIL import Image
# import cv2

MIN_DISTANCE = 20


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
            print("Left", self.is_free(self._sensor_values[key]))
        elif key == "S2":
            self._perception["left"] = self.is_free(self._sensor_values[key])
            print("Front", self.is_free(self._sensor_values[key]))
        elif key == "S3":
            self._perception["right"] = self.is_free(self._sensor_values[key])
            print("Right", self.is_free(self._sensor_values[key]))
        elif key == "orientation":
            print("Orientation", str(self._sensor_values[key]))
            if self._sensor_values[key]:
                value_list = json.loads(self._sensor_values[key])
                angle = self.convert_byte_to_angle(value_list[1])
                self._perception["orientation"] = angle
        elif key == "position":
            if key2 == "x":
                self._perception["position-x"] = self._sensor_values["position-x"]
            elif key2 == "y":
                self._perception["position-y"] = self._sensor_values["position-y"]
        elif key == "camera":
            print("immagine")
            #image = base64.b64decode(self._sensor_values["camera"])
            #self._perception["green"] = self.is_green_object_present(image)

            # self._perception["green"] = self.detect_green_object(self._sensor_values["camera"])

    def is_green_object_present(self, frame):
        from io import BytesIO

        # Decodificare il frame (bytes) in un'immagine PIL
        image = Image.open(BytesIO(frame)).convert("RGB")

        # Convertire l'immagine in spazio colore HSV
        hsv_image = Image.fromarray(frame).convert("HSV")
        hsv_array = np.array(hsv_image)

        # Definire i limiti inferiori e superiori per il colore verde in HSV
        lower_green = np.array([35, 100, 100])
        upper_green = np.array([85, 255, 255])

        # Creare una maschera per il colore verde
        mask = ((hsv_array[:, :, 0] >= lower_green[0]) & (hsv_array[:, :, 0] <= upper_green[0]) &
                (hsv_array[:, :, 1] >= lower_green[1]) & (hsv_array[:, :, 1] <= upper_green[1]) &
                (hsv_array[:, :, 2] >= lower_green[2]) & (hsv_array[:, :, 2] <= upper_green[2]))

        # Verifica se ci sono abbastanza pixel verdi per essere considerato un oggetto
        green_pixel_count = np.sum(mask)
        return green_pixel_count > 500  # Soglia arbitraria per considerare un oggetto

    """
    def detect_green_object(self, frame):
        # Convertire il frame in spazio colore HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Definire i limiti inferiori e superiori per il colore verde in HSV
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])

        # Creare una maschera per il colore verde
        mask = cv2.inRange(hsv, lower_green, upper_green)

        # Trovare i contorni degli oggetti verdi
        _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours is None:
            return False

        # Controllare se esiste almeno un contorno con una certa area minima
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filtrare contorni piccoli
                return True

        return False
    """

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

    def find_name(self, value, value2):
        if value == "S1":
            return "front"
        elif value == "S2":
            return "left"
        elif value == "S3":
            return "right"
        elif value == "orientation":
            return value
        elif value == "position" and value2 == "x":
            return "position-x"
        elif value == "position" and value2 == "y":
            return "position-y"
        # elif value == "camera":
            # return "green"


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
    if sensor_name[1] != 'camera':
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
        print("ingore")


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
