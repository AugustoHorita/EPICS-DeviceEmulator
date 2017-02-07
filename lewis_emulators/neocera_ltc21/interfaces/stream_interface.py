import re

from lewis.adapters.stream import StreamAdapter, Cmd

from lewis_emulators.neocera_ltc21.constants import HEATER_INDEX, CONTROL_TYPE_MAX, CONTROL_TYPE_MIN, ANALOG_INDEX
from lewis_emulators.neocera_ltc21.device_errors import NeoceraDeviceErrors
from lewis_emulators.neocera_ltc21.states import MonitorState, ControlState


class CmdBuilder(object):
    """
    Build a command for the stream adapter
    """

    def __init__(self, target_method, arg_sep=",", ignore=""):
        """
        Create a builder. Use build to create the final objecy
        Args:
            target_method: name of the method target to call when the reg ex matches
            arg_sep: seperators between the arguments
            ignore: set of characters to ignore between text and arguments

        Returns:

        """
        self._target_method = target_method
        self._arg_sep = arg_sep
        self._current_sep = ""
        self._ignore = "[{0}]*".format(ignore)
        self._reg_ex = self._ignore

    def escape(self, text):
        """
        Add some text to the regex which is esacped
        Args:
            text: text to add

        Returns: builder

        """
        self._reg_ex += re.escape(text) + self._ignore
        return self

    def arg(self, arg_regex):
        """
        Add an argument to the command
        Args:
            arg_regex: regex for the argument (capture group will be added)

        Returns: builder

        """
        self._reg_ex += self._current_sep + "(" + arg_regex + ")" + self._ignore
        self._current_sep = self._arg_sep
        return self

    def float(self):
        """
        Add a float argument
        Returns: builder

        """
        return self.arg(r"[+-]?\d+\.?\d*")

    def digit(self):
        """
        Add a single digit argument
        Returns: builder

        """
        return self.arg(r"\d")

    def int(self):
        """
        Add an integer argument
        Returns: builder

        """
        return self.arg(r"\d+")

    def build(self, *args, **kwargs):
        """
        Builds the CMd object based on the target and regular expression
        Args:
            *args: arguments to pass to Cmd constructor
            **kwargs: key word arguments to pass to Cmd constructor

        Returns: Cmd object

        """
        return Cmd(self._target_method, self._reg_ex, *args, **kwargs)


class NeoceraStreamInterface(StreamAdapter):
    """
    Stream interface for the serial port
    """

    commands = {
        CmdBuilder("get_state", arg_sep=",", ignore=r"\r\n\s").escape("QISTATE?").build(),
        CmdBuilder("set_state_monitor", arg_sep=",", ignore=r"\r\n\s").escape("SMON").build(),
        CmdBuilder("set_state_control", arg_sep=",", ignore=r"\r\n\s").escape("SCONT").build(),
        CmdBuilder("get_temperature_and_unit", arg_sep=",", ignore=r"\r\n\s").escape("QSAMP?").digit().build(),
        CmdBuilder("get_setpoint_and_unit", arg_sep=",", ignore=r"\r\n\s").escape("QSETP?").digit().build(),
        CmdBuilder("set_setpoint", arg_sep=",", ignore=r"\r\n\s").escape("SETP").digit().float().build(),
        CmdBuilder("get_output_config", arg_sep=",", ignore=r"\r\n\s").escape("QOUT?").digit().build(),
        CmdBuilder("set_heater_control", arg_sep=",", ignore=r"\r\n\s").escape("SHCONT").digit().build(),
        CmdBuilder("set_analog_control", arg_sep=",", ignore=r"\r\n\s").escape("SACONT").digit().build(),
        CmdBuilder("get_heater", arg_sep=",", ignore=r"\r\n\s").escape("QHEAT?").build(),
        CmdBuilder("get_pid", arg_sep=",", ignore=r"\r\n\s").escape("QPID?").digit().build(),
        CmdBuilder("set_pid_heater", arg_sep=",", ignore=r"\r\n\s").escape("SPID1,").float().float().float().float().float().build(),
        CmdBuilder("set_pid_analog", arg_sep=",", ignore=r"\r\n\s").escape("SPID2,").float().float().float().float().float().float().build()
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

    def get_setpoint_and_unit(self, output_number):
        """

        Args:
            output_number: the number of set point top return; 1=HEATER, 2=ANALOG

        Returns: setpoint with unit

        """
        return self._get_indexed_value_with_unit(self._device.setpoints, output_number)

    def set_setpoint(self, output_number, value):
        """
        Set the setpoint.
        Args:
            output_number: output number; 1=HEATER, 2=ANALOG
            value: value to set it to

        Returns: blank

        """
        try:
            output_index = int(output_number) - 1
            setpoint = float(value)

            self._device.setpoints[output_index] = setpoint
        except (IndexError, ValueError, TypeError):
            print "Error: invalid output number, '{0}', or setpoint value, '{1}'".format(output_number, value)
            self._device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)
            return ""

    def get_output_config(self, output_number):
        """
        Reply to output configuration query.
            # Example QOUT?1;   produces -> 2;4;3;
            # Example QOUT?2;   produces -> 3;5;

        Args:
            output_number: The output number being queries; 1 HEATER, 2 Analogue

        Returns: configuration as a string; sensor source;control;heater_range

        """

        device = self._device
        try:
            output_index = int(output_number) - 1

            output_config = "{sensor_source};{control}".format(
                sensor_source=device.sensor_source[output_index], control=device.control[output_index])

            if output_index == HEATER_INDEX:
                output_config += ";{heater_range}".format(heater_range=device.heater_range)

            return output_config

        except (IndexError, ValueError, TypeError):
            print "Error: invalid output number, '{0}'".format(output_number)
            device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)
            return ""

    def set_heater_control(self, control_type_number):
        """
        Set the heater output control
        Args:
            control_type_number: control type to set the heater to

        Returns: None

        """

        self._set_output_control(HEATER_INDEX, control_type_number)

    def set_analog_control(self, control_type_number):
        """
        Set the analog output control
        Args:
            control_type_number: control type to set the heater to

        Returns: None

        """

        self._set_output_control(ANALOG_INDEX, control_type_number)

    def _set_output_control(self, output_index, control_type_number):
        """
        Set the output control for either the heater or the analog output
        Args:
            output_index: output index
            control_type_number: control type to set

        Returns: None

        """
        device = self._device
        try:
            control_type = int(control_type_number)

            if control_type < CONTROL_TYPE_MIN[output_index] or \
                    control_type > CONTROL_TYPE_MAX[output_index]:
                raise ValueError("Bad control type number")

            self._device.control[output_index] = control_type

        except (IndexError, ValueError, TypeError):
            print "Error: invalid control type number for output {output}, '{0}'".format(
                control_type_number, output=output_index)
            device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)

    def get_heater(self):
        """

        Returns: Heater output

        """
        return "{0:5.1f}".format(self._device.heater)

    def get_pid(self, output_number):
        """
        Get the PID and other info of the output. Information is
            P, I, D, fixed power settting,
            for heater: power limit
            for analog: gain and offset

            Exmaples:
              QPID?1; -> 24.999;32.;8.;0.0;100.;
              QPID?2; -> 99.999;10.;0.0;0.0;1.;0.0;

        Args:
            output_number: output number;

        Returns: various info as a string

        """
        device = self._device
        try:
            output_index = int(output_number) - 1

            pid_output = "{P:f};{I:f};{D:f};{fixed_power:f}".format(**device.pid[output_index])

            if output_index == HEATER_INDEX:
                return "{pid_output};{limit:f}".format(pid_output=pid_output, **device.pid[output_index])
            else:
                return "{pid_output};{gain:f};{offset:f}".format(pid_output=pid_output, **device.pid[output_index])

        except (IndexError, ValueError, TypeError):
            print "Error: invalid output number, '{output}'".format(output=output_number)
            device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)

    def set_pid_heater(self, p, i, d, fixed_power, limit):
        """
        Set the pid settings for the heater
        Args:
            p: p
            i: i
            d: d
            fixed_power: fixed power
            limit: limit of the heater

        Returns: None

        """
        pid_settings = self._device.pid[HEATER_INDEX]
        try:
            self._set_pid(p, i, d, fixed_power, pid_settings)
            limit_as_float = float(limit)
            if limit_as_float < 0.0 or limit_as_float > 100.0:
                raise ValueError("Outside allowed heater range")
            pid_settings["limit"] = limit_as_float

        except (IndexError, ValueError, TypeError):
            print "Error: in pid settings for heater"
            self._device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)

    def set_pid_analog(self, p, i, d, fixed_power, gain, offset):
        """
        Set the pid settings for the analog output
        Args:
            p: p
            i: i
            d: d
            fixed_power: fixed power
            gain: gain of the output
            offset: offset for the output

        Returns: None

        """
        pid_settings = self._device.pid[ANALOG_INDEX]
        try:
            self._set_pid(p, i, d, fixed_power, pid_settings)
            pid_settings["gain"] = float(gain)
            pid_settings["offset"] = float(offset)

        except (IndexError, ValueError, TypeError):
            print "Error: in pid settings for analog"
            self._device.error = NeoceraDeviceErrors(NeoceraDeviceErrors.BAD_PARAMETER)

    def _set_pid(self, p, i, d, fixed_power, pid_settings):
        """
        Common function to set p,i,d and power
        Args:
        Args:
            p: p
            i: i
            d: d
            fixed_power: fixed power
            pid_settings: in which to set them

        Returns: None

        """
        pid_settings["P"] = float(p)
        pid_settings["I"] = float(i)
        pid_settings["D"] = float(d)
        pid_settings["fixed_power"] = float(fixed_power)

    def handle_error(self, request, error):
        """

        Handles errors.

        Args:
            request:
            error:

        """
        print "An error occurred at request " + repr(request) + ": " + repr(error)
