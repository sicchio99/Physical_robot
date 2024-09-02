import time
import serial


class ColorSensorReader:
    def __init__(self, port='/dev/ttyUSB2', baudrate=9600, timeout=2):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Attendere che la connessione seriale sia pronta)

    def read_color(self):
        """
        Legge i dati dalla porta seriale e restituisce il colore rilevato dal sensore.
        """
        if self.ser.in_waiting > 0:
            # Legge la linea dalla seriale
            line = self.ser.readline().decode('utf-8', errors="ignore").rstrip()
            return line  # Restituisce il colore letto
        return None

    def close(self):
        """Chiude la connessione seriale."""
        self.ser.close()


if __name__ == "__main__":
    sensor = ColorSensorReader()
    while True:
        color = sensor.read_color()
        print("Colore: ", color)
        time.sleep(1)
