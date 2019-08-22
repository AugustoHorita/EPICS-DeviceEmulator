from lewis.adapters.stream import StreamInterface, Cmd

from lewis_emulators.utils.command_builder import CmdBuilder


class LinmotStreamInterface(StreamInterface):

    in_terminator = "\r\n"
    out_terminator = "\r"

    readtimeout = 5000

    def __init__(self):

        super(LinmotStreamInterface, self).__init__()
        # Commands that we expect via serial during normal operation
        self. commands = {
            CmdBuilder(self.set_position).escape("!SP").int().escape("A").eos().build(),
            CmdBuilder(self.get_position).escape("!GPA").eos().build(),
            CmdBuilder(self.get_actual_speed_resolution).escape("!VIA").eos().build(),
            CmdBuilder(self.get_motor_warn_status).escape("!EWA").eos().build(),
            CmdBuilder(self.get_motor_error_status).escape("!EEA").eos().build(),
            CmdBuilder(self.set_maximal_speed).escape("!SV").int().escape("A").eos().build(), #SV
            CmdBuilder(self.set_maximal_acceleration).escape("!SA").int().escape("A").eos().build(), #SA
            }

    def handle_error(self, request, error):
        err_string = "command was: {}, error was: {}: {}\n".format(request, error.__class__.__name__, error)
        print(err_string)
        self.log.error(err_string)
        return err_string

    def set_position(self, target_position):
        self.device.target_position = target_position
        self.device.new_action = True
        self.device.position_reached = False
        return "#"

    def get_position(self):
        return "#{position}".format(position=self.device.position)

    def get_actual_speed_resolution(self):
        return "#{velocity}".format(velocity=self.device.velocity)

    def get_motor_warn_status(self):
        return "#{motor_warn_status}".format(motor_warn_status=self.device.motor_warn_status)

    def get_motor_error_status(self):
        return "#{motor_error_status}".format(motor_error_status=self.device.motor_error_status)

    def set_maximal_speed(self, speed):
        self.device.maximal_speed = speed
        return "#"

    def set_maximal_acceleration(self, acceleration):
        self.device.maximal_acceleration = acceleration
        return "#"

    def catch_all(self):
        pass
