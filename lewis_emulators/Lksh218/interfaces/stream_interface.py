from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis_emulators.utils.command_builder import CmdBuilder


def if_connected(f):
    def wrapper(*args):
        connected = getattr(args[0], "_device").connected
        if connected:
            result = f(*args)
        else:
            result = None
        return result
    return wrapper


@has_log
class Lakeshore218StreamInterface(StreamInterface):
    """
    Stream interface for the serial port
    """

    in_terminator = "\r\n"
    out_terminator = "\r\n"

    commands = {
        CmdBuilder("get_temp").escape("KRDG? ").arg("[1-8]").build(),
        CmdBuilder("get_sensor").escape("SRDG? ").arg("[1-8]").build(),
        CmdBuilder("get_temp_all").escape("KRDG? 0").build(),
        CmdBuilder("get_sensor_all").escape("SRDG? 0").build()
    }

    @if_connected
    def get_temp(self, number):
        number = int(number)
        temperature = self._device.get_temp(number)
        return temperature

    @if_connected
    def get_sensor(self, number):
        number = int(number)
        sensor_reading = self._device.get_sensor(number)
        return sensor_reading

    @if_connected
    def get_temp_all(self):
        return self._device.temp_all

    @if_connected
    def get_sensor_all(self):
        return self._device.sensor_all
