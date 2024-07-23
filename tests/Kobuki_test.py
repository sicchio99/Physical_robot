import serial as ser
import threading

import serial.tools.list_ports as lsports


class Kobuki:
    __in_buff = []
    __temp = bytearray()
    button_0 = False
    button_1 = False
    button_2 = False
    right_bumper = False
    left_bumper = False
    center_bumper = False
    right_wheel_dropped = False
    left_wheel_dropped = False
    both_wheel_dropped = False
    __basic_sensor = []
    __docking_IR = []
    __inertial_sensor = []
    __cliffsensor = []
    __current = []
    __gyro = []
    __general_purpose_input = []
    __th1 = None

    def getKobukiPort(self):
        ports = lsports.comports()
        print(ports)
        for kport, desc, hwid in sorted(ports):
            print(kport)
            if "USB Serial Port" in desc or "Kobuki" in desc:
                print("Kobuki is connected in the following port:")
                print("{} {} [{}]".format(kport, desc, hwid))
                try:
                    Kobuki.seri = ser.Serial(port=kport, baudrate=115200)
                    return Kobuki.seri
                except ser.SerialException as e:
                    print(f"Error opening serial port: {e}")
        else:
            raise Exception("Kobuki is not connected")

    def __init__(self):
        self.getKobukiPort()
        self.__th1 = threading.Thread(target=self.read_data)
        self.__th1.start()

    def move(self, left_velocity, right_velocity, rotate):
        if rotate == 0:
            # Movimento normale
            botspeed = (left_velocity + right_velocity) / 2
            if left_velocity == right_velocity:
                botradius = 0
            else:
                botradius = (230 * (left_velocity + right_velocity)) / (2 * (right_velocity - left_velocity))
        elif rotate == 1:  # Rotazione a sinistra
            # Rotazione sul posto
            botspeed = left_velocity
            botradius = 1  # Raggio 1 indica rotazione sul posto senso antiorario
        elif rotate == -1:  # Rotazione a destra
            botspeed = left_velocity
            botradius = -1  # Raggio 1 indica rotazione sul posto senso antiorario

        cs = 0
        barr = bytearray([170, 85, 6, 1, 4])
        barr += int(botspeed).to_bytes(2, byteorder='little', signed=True)
        barr += int(botradius).to_bytes(2, byteorder='little', signed=True)

        for i in range(2, len(barr) - 1):
            cs = cs ^ barr[i]
        barr += cs.to_bytes(1, byteorder='big')

        Kobuki.seri.write(barr)

    # modificata
    def read_data(self):
        while True:
            if Kobuki.seri.in_waiting > 0:
                if int.from_bytes(Kobuki.seri.read(2), byteorder='little') == 333:
                    __temp = Kobuki.seri.read(200)
                    __in_buff = [x for x in __temp]

                    for data in range(0, len(__in_buff) - 1):
                        if __in_buff[data] == 170 and __in_buff[data + 1] == 85:
                            Kobuki.__general_purpose_input = __in_buff[data - 19:]

                    Kobuki.__basic_sensor = __in_buff[1:16]
                    Kobuki.__docking_IR = __in_buff[15:21]
                    Kobuki.__inertial_sensor = __in_buff[21:30]
                    Kobuki.__cliffsensor = __in_buff[30:38]
                    Kobuki.__current = __in_buff[38:42]
                    Kobuki.__gyro = __in_buff[42:44 + __in_buff[43]]

    def inertial_sensor_data(self):
        angle = {}
        angle.update({'angle': Kobuki.__inertial_sensor[2:4]})
        angle.update({'anglerate': Kobuki.__inertial_sensor[4:6]})
        return angle

    def gyro_intconverted_data(self):

        x_axis = []
        y_axis = []
        z_axis = []
        x_axis_converted = []
        y_axis_converted = []
        z_axis_converted = []
        gyro = {}
        gyro.update({'Size of data field': Kobuki.__gyro[1]})
        gyro.update({'Frame id': Kobuki.__gyro[2]})
        gyro.update({'Followed data length': Kobuki.__gyro[3]})
        nvalue = 2
        count = 0
        iteration = 4
        while count != 4 and iteration <= (Kobuki.__gyro[3] * 2) + nvalue:
            if count == 0:
                x_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            elif count == 1:
                y_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            elif count == 2:
                z_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            if count == 3:
                count = 0
        for data in x_axis:
            x_axis_converted.append(int.from_bytes(data, 'little'))
        for data in y_axis:
            y_axis_converted.append(int.from_bytes(data, 'little'))
        for data in z_axis:
            z_axis_converted.append(int.from_bytes(data, 'little'))
        gyro.update({'x_axis_converted_to_int: ': x_axis_converted})
        gyro.update({'y_axis_converted_to_int: ': y_axis_converted})
        gyro.update({'z_axis_converted_to_int: ': z_axis_converted})
        return gyro

    def gyro_raw_data(self):

        x_axis = []
        y_axis = []
        z_axis = []
        gyro = {}
        gyro.update({'Size of data field': Kobuki.__gyro[1]})
        gyro.update({'Frame id': Kobuki.__gyro[2]})
        gyro.update({'Followed data length': Kobuki.__gyro[3]})
        nvalue = 2
        count = 0
        iteration = 4
        while count != 4 and iteration <= (Kobuki.__gyro[3] * 2) + nvalue:
            if count == 0:
                x_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            elif count == 1:
                y_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            elif count == 2:
                z_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            if count == 3:
                count = 0

        gyro.update({'x_axis_rawdata: ': x_axis})
        gyro.update({'y_axis_rawdata: ': y_axis})
        gyro.update({'z_axis_rawdata: ': z_axis})
        return gyro

    def gyro_velocity_data(self):

        digit_to_dps = 0.00875
        x_axis = []
        y_axis = []
        z_axis = []
        x_axis_velocity = []
        y_axis_velocity = []
        z_axis_velocity = []
        gyro = {}
        gyro.update({'Size of data field': Kobuki.__gyro[1]})
        gyro.update({'Frame id': Kobuki.__gyro[2]})
        gyro.update({'Followed data length': Kobuki.__gyro[3]})
        nvalue = 2
        count = 0
        iteration = 4
        while count != 4 and iteration <= (Kobuki.__gyro[3] * 2) + nvalue:
            if count == 0:
                x_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            elif count == 1:
                y_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            elif count == 2:
                z_axis.append(Kobuki.__gyro[iteration:iteration + nvalue])
                count = count + 1
                iteration = iteration + nvalue
            if count == 3:
                count = 0
        for data in x_axis:
            for innerdata in data:
                y_axis_velocity.append((digit_to_dps * -1) * innerdata)
        for data in y_axis:
            for innerdata in data:
                x_axis_velocity.append(digit_to_dps * innerdata)
        for data in z_axis:
            for innerdata in data:
                z_axis_velocity.append(digit_to_dps * innerdata)
        gyro.update({'angular velocity of x: ': x_axis_velocity})
        gyro.update({'angular velocity of y: ': y_axis_velocity})
        gyro.update({'angular velocity of z: ': z_axis_velocity})
        return gyro

    def kobukistart(self, start):
        th2 = threading.Thread(target=start)
        th2.start()
        th2.join()
        self.__th1.join()
