import re

from lewis.adapters.stream import StreamAdapter, Cmd

from lewis_emulators.neocera_ltc21.device_errors import NeoceraDeviceErrors
from lewis_emulators.neocera_ltc21.states import MonitorState, ControlState


def get_regex(command, *args):

    """

    Takes a command and optional arguments and turns then into a regex for lewis

    Args:
        command: the command to turn into a regex

    Returns: a regex for lewis

    """

    command = re.escape(command)
    args_regex = ""
    comma = ""
    for arg in args:
        args_regex += "{stripped}{comma}({arg})".format(arg=arg, stripped=r"[\r\n\s]*", comma=comma)
        comma = ","

    return "{stripped}{command}{args_regex}{stripped}".format(
        stripped=r"[\r\n\s]*", args_regex=args_regex, command=command)


class NeoceraStreamInterface(StreamAdapter):
    """
    Stream interface for the serial port
    """

    commands = {
        Cmd("get_state", get_regex("QISTATE?")),
        Cmd("set_state_monitor", get_regex("SMON")),
        Cmd("set_state_control", get_regex("SCONT")),
        Cmd("get_temperature_and_unit", get_regex("QSAMP?", "\d")),
        Cmd("get_setpoint_and_unit", get_regex("QSETP?", "\d")),
        Cmd("set_setpoint", get_regex("SETP", "\d", "[+-]?\d+\.?\d+")),
    }

    in_terminator = ";"
    out_terminator = ";\n"

    def get_state(self):

        """
        Gets the current state of the device

        Returns: a single character string containing a number which represents the state of the device

        """

        if self._device.state == MonitorState.NAME:
            return "0"
        elif self._device.state == ControlState.NAME:
            return "1"

    def get_temperature_and_unit(self, sensor_number):
        """
        Return the temperature and unit for the sensor number given.
        Args:
            sensor_number: sensor number

        Returns: formatted temperature and unit for the device

        """
        return self._get_indexed_value_with_unit(self._device.temperatures, sensor_number)

    def _get_indexed_value_with_unit(self, device_values, item_number):
        """
        Get a temperature like value back from device temperatures in the format produced by the device
        Args:
            device_values: device value, e.g. temperatures list
            item_number: item to return

        Returns: temp and units; e.g. setpoint 1.2K

        """
        try:
            sensor_index = int(item_number) - 1
            device_value = device_values[sensor_index]

            # for temperatures it can not read
            if device_value is None:
                return " ------ "

            unit = self._device.units[sensor_index]

            return "{0:8f}{1:1s}".format(device_value, unit)

        except (IndexError, ValueError, TypeError):
            print "Error: invalid sensor number requested '{0}'".format(item_number)
            self._device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)
            return ""

    def get_setpoint_and_unit(self, set_point_number):
        """

        Args:
            set_point_number: the number of set point top return; 1=HEATER, 2=ANALOG

        Returns: setpoint with unit

        """
        return self._get_indexed_value_with_unit(self._device.setpoints, set_point_number)

    def set_setpoint(self, set_point_number, value):
        """
        Set the setpoint.
        Args:
            set_point_number: set point number; 1=HEATER, 2=ANALOG
            value: value to set it to

        Returns: blank

        """
        try:
            sensor_number = int(set_point_number) - 1
            setpoint = float(value)

            self._device.setpoints[sensor_number] = setpoint
        except (IndexError, ValueError, TypeError):
            print "Error: invalid sensor number, '{0}', or setpoint value, '{1}'".format(set_point_number, value)
            self._device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)
            return ""


    def handle_error(self, request, error):
        """

        Handles errors.

        Args:
            request:
            error:

        """
        print "An error occurred at request " + repr(request) + ": " + repr(error)
