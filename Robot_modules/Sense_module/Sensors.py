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
            line = self.ser.readline().decode('utf-8', errors="ignore").strip()
            sensor_id, distance = line.split(",")
            return {'sensor_id': sensor_id, 'distance': float(distance)}
        return None

    def close(self):
        """Chiude la connessione seriale."""
        self.ser.close()


"""
try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors="ignore").strip()
            sensor_id, distance = line.split(",")
            print(f"Sensore: {sensor_id}, Distance: {distance}")
except KeyboardInterrupt:
    print("\nInterrotto")
finally:
    ser.close()
"""
