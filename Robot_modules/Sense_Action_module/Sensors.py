import time
import serial


class UltrasonicSensorReader:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=2):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Attendere che la connessione seriale sia pronta)

    def read_sensor_data(self):
        """
        Legge i dati dalla porta seriale e restituisce un dizionario
        contenente l'ID del sensore e la distanza misurata.
        """
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8', errors="ignore").rstrip()
            sensor_id, distance = line.split(",")
            return {'sensor_id': sensor_id, 'distance': float(distance)}
        return None

    def close(self):
        """Chiude la connessione seriale."""
        self.ser.close()


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
