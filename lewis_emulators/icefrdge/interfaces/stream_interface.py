from lewis.adapters.stream import StreamInterface, Cmd
from lewis_emulators.utils.command_builder import CmdBuilder
from lewis.core.logging import has_log
from lewis_emulators.utils.constants import ACK, ENQ


@has_log
class IceFridgeStreamInterface(StreamInterface):

    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("set_auto_temp_setpoint").escape("AUTO TSET=").float().eos().build(),
        CmdBuilder("get_auto_temp_set_RBV").escape("AUTO TSET?").eos().build(),
        CmdBuilder("get_auto_temp_set_RBV").escape("AUTO TEMP?").eos().build(),
        CmdBuilder("set_manual_temp_setpoint").escape("MANUAL TSET=").float().eos().build(),
        CmdBuilder("get_manual_temp_set_RBV").escape("MANUAL TSET?").eos().build(),
        CmdBuilder("get_manual_temp_set_RBV").escape("MANUAL TEMP?").eos().build(),
        CmdBuilder("get_cryo_temps").escape("CRYO-TEMPS?").eos().build(),
        CmdBuilder("set_loop1_temp_setpoint").escape("CRYO-TSET=1,").float().eos().build(),
        CmdBuilder("get_loop1_temp_setpoint").escape("CRYO-TSET1?").eos().build(),
        CmdBuilder("set_loop2_temp_setpoint").escape("CRYO-TSET=2,").float().eos().build(),
        CmdBuilder("get_loop2_temp_setpoint").escape("CRYO-TSET2?").eos().build(),
        CmdBuilder("set_loop1_proportional_setpoint").escape("CRYO-P=1,").float().eos().build(),
        CmdBuilder("get_loop1_proportional_setpoint").escape("CRYO-P1?").eos().build(),
        CmdBuilder("set_loop2_proportional_setpoint").escape("CRYO-P=2,").float().eos().build(),
        CmdBuilder("get_loop2_proportional_setpoint").escape("CRYO-P2?").eos().build(),
        CmdBuilder("set_loop1_integral_setpoint").escape("CRYO-I=1,").float().eos().build(),
        CmdBuilder("get_loop1_integral_setpoint").escape("CRYO-I1?").eos().build(),
        CmdBuilder("set_loop2_integral_setpoint").escape("CRYO-I=2,").float().eos().build(),
        CmdBuilder("get_loop2_integral_setpoint").escape("CRYO-I2?").eos().build(),
        CmdBuilder("set_loop1_derivative_setpoint").escape("CRYO-D=1,").float().eos().build(),
        CmdBuilder("get_loop1_derivative_setpoint").escape("CRYO-D1?").eos().build(),
        CmdBuilder("set_loop2_derivative_setpoint").escape("CRYO-D=2,").float().eos().build(),
        CmdBuilder("get_loop2_derivative_setpoint").escape("CRYO-D2?").eos().build(),

        CmdBuilder("set_loop1_ramp_rate_setpoint").escape("CRYO-RAMP=1,").float().eos().build(),
        CmdBuilder("get_loop1_ramp_rate_setpoint").escape("CRYO-RAMP1?").eos().build(),
        CmdBuilder("set_loop2_ramp_rate_setpoint").escape("CRYO-RAMP=2,").float().eos().build(),
        CmdBuilder("get_loop2_ramp_rate_setpoint").escape("CRYO-RAMP2?").eos().build()
    }

    in_terminator = "\n"
    out_terminator = "\n"

    def handle_error(self, request, error):
        """
        Prints and logs an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.
        Returns:
            String: The error string.
        """
        err_string = "command was: \"{}\", error was: {}: {}\n".format(request, error.__class__.__name__, error)
        print(err_string)
        self.log.error(err_string)
        return err_string

    def set_auto_temp_setpoint(self, temp_setpoint):
        self._device.auto_temp_setpoint = temp_setpoint

    def get_auto_temp_set_RBV(self):
        return self._device.auto_temp_setpoint

    def set_manual_temp_setpoint(self, temp_setpoint):
        self._device.manual_temp_setpoint = temp_setpoint

    def get_manual_temp_set_RBV(self):
        return self._device.manual_temp_setpoint

    def get_cryo_temps(self):
        return "CRYO-TEMPS={},{},{},{}".format(self._device.vti_temp1, self._device.vti_temp2, self._device.vti_temp3,
                                               self._device.vti_temp4)

    def set_loop1_temp_setpoint(self, temp_setpoint):
        self._device.vti_loop1_temp_setpoint = temp_setpoint

    def get_loop1_temp_setpoint(self):
        return "CRYO-TSET1={}".format(self._device.vti_loop1_temp_setpoint)

    def set_loop2_temp_setpoint(self, temp_setpoint):
        self._device.vti_loop2_temp_setpoint = temp_setpoint

    def get_loop2_temp_setpoint(self):
        return "CRYO-TSET2={}".format(self._device.vti_loop2_temp_setpoint)

    def set_loop1_proportional_setpoint(self, proportional_setpoint):
        self._device.vti_loop1_proportional = proportional_setpoint

    def get_loop1_proportional_setpoint(self):
        return "CRYO-P1={}".format(self._device.vti_loop1_proportional)

    def set_loop2_proportional_setpoint(self, proportional_setpoint):
        self._device.vti_loop2_proportional = proportional_setpoint

    def get_loop2_proportional_setpoint(self):
        return "CRYO-P2={}".format(self._device.vti_loop2_proportional)

    def set_loop1_integral_setpoint(self, integral_setpoint):
        self._device.vti_loop1_integral = integral_setpoint

    def get_loop1_integral_setpoint(self):
        return "CRYO-I1={}".format(self._device.vti_loop1_integral)

    def set_loop2_integral_setpoint(self, integral_setpoint):
        self._device.vti_loop2_integral = integral_setpoint

    def get_loop2_integral_setpoint(self):
        return "CRYO-I2={}".format(self._device.vti_loop2_integral)

    def set_loop1_derivative_setpoint(self, derivative_setpoint):
        self._device.vti_loop1_derivative = derivative_setpoint

    def get_loop1_derivative_setpoint(self):
        return "CRYO-D1={}".format(self._device.vti_loop1_derivative)

    def set_loop2_derivative_setpoint(self, derivative_setpoint):
        self._device.vti_loop2_derivative = derivative_setpoint

    def get_loop2_derivative_setpoint(self):
        return "CRYO-D2={}".format(self._device.vti_loop2_derivative)

    def set_loop1_ramp_rate_setpoint(self, ramp_rate_setpoint):
        self._device.vti_loop1_ramp_rate = ramp_rate_setpoint

    def get_loop1_ramp_rate_setpoint(self):
        return "CRYO-RAMP1={}".format(self._device.vti_loop1_ramp_rate)

    def set_loop2_ramp_rate_setpoint(self, ramp_rate_setpoint):
        self._device.vti_loop2_ramp_rate = ramp_rate_setpoint

    def get_loop2_ramp_rate_setpoint(self):
        return "CRYO-RAMP2={}".format(self._device.vti_loop2_ramp_rate)

