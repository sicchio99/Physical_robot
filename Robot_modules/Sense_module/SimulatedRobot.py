from coppeliasim_zmqremoteapi_client import RemoteAPIClient
from typing import Any, List

MY_SIM_HOST = "host.docker.internal"


class SimulatedPioneerBody:
    _sim: Any
    _cSim_client: Any
    _my_sensors_values: List
    _robot_handle: Any

    def __init__(self, name: str):
        self._my_name = name
        # zmqRemoteApi connection
        print("Connecting to simulator...")
        self._cSim_client = RemoteAPIClient(host=MY_SIM_HOST)
        self._sim = self._cSim_client.require('sim')
        print("Connected to SIM")
        self._robot_handle = self._sim.getObjectHandle("/PioneerP3DX")
        self._my_sensors_values = []
        front_sensors = [
            self._sim.getObjectHandle("./ultrasonicSensor[0]"),
            self._sim.getObjectHandle("./ultrasonicSensor[1]"),
            self._sim.getObjectHandle("./ultrasonicSensor[2]"),
            self._sim.getObjectHandle("./ultrasonicSensor[3]"),
            self._sim.getObjectHandle("./ultrasonicSensor[4]"),
            self._sim.getObjectHandle("./ultrasonicSensor[5]"),
            self._sim.getObjectHandle("./ultrasonicSensor[6]"),
            self._sim.getObjectHandle("./ultrasonicSensor[7]")
        ]
        self._my_sensors_values.append(front_sensors)
        back_sensors = [
            self._sim.getObject("./ultrasonicSensor[8]"),
            self._sim.getObject("./ultrasonicSensor[9]"),
            self._sim.getObject("./ultrasonicSensor[10]"),
            self._sim.getObject("./ultrasonicSensor[11]"),
            self._sim.getObject("./ultrasonicSensor[12]"),
            self._sim.getObject("./ultrasonicSensor[13]"),
            self._sim.getObject("./ultrasonicSensor[14]"),
            self._sim.getObject("./ultrasonicSensor[15]")
        ]
        self._my_sensors_values.append(back_sensors)
        connected_sensors = [
            self._sim.getObject("/Vision_sensor")
        ]
        self._my_sensors_values.append(connected_sensors)
        print("SIM objects referenced")

    def _read_proximity_sensors(self, i: int):
        # i = 0 : front sensors
        # i = 1 : back sensors
        assert 0 <= i <= 1, "incorrect sensor array"
        values = []
        for sens in self._my_sensors_values[i]:
            _, dis, _, _, _ = self._sim.readProximitySensor(sens)
            values.append(dis)
        return values

    def _read_vision_sensors(self, i: int):
        assert i == 2, "incorrect sensor array"
        values = []
        for sens in self._my_sensors_values[i]:
            image, resolution = self._sim.getVisionSensorImg(sens)
            values.append((image, resolution))
        return values

    def get_robot_orientation(self):
        orientation = self._sim.getObjectOrientation(self._robot_handle, -1)
        return orientation[2]  # Returns the yaw angle

    def get_robot_position(self):
        position = self._sim.getObjectPosition(self._robot_handle, -1)
        return position  # Returns the position as [x, y, z]

    def sense(self):
        try:
            vision_values = self._read_vision_sensors(2)  # only vision sensors
            front_values = self._read_proximity_sensors(
                0)  # only front sensors
            orientation = self.get_robot_orientation()
            position = self.get_robot_position()
            return vision_values, front_values, orientation, position
        except Exception as e:
            print(e)

    def start(self):
        self._sim.startSimulation()

    def stop(self):
        self._sim.stopSimulation()
