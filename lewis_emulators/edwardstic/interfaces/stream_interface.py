from lewis.adapters.stream import StreamInterface
from lewis_emulators.utils.command_builder import CmdBuilder
from lewis.core.logging import has_log
from lewis_emulators.utils.replies import conditional_reply
from ..device import PumpStates, AlertStates, PriorityStates


PUMPSTATES_MAP = {
    0: PumpStates.stopped,
    1: PumpStates.starting_delay,
    5: PumpStates.accelerating,
    4: PumpStates.running,
    2: PumpStates.stopping_short_delay,
    3: PumpStates.stopping_normal_delay,
    6: PumpStates.fault_braking,
    7: PumpStates.braking,
}

PRIORITYSTATES_MAP = {
    PriorityStates.OK: 0,
    PriorityStates.Warning: 1,
    PriorityStates.Alarm: 3
    }


def reverse_dict_lookup(dictionary, value_to_find):
    """
    Looks up the key for the supplied value in dictionary dict.

    Args:
        dict: dictionary, the dictionary to do the reverse lookup
        value: the value to find in the dictionary
    
    Raises:
        KeyError if value does not exist in the dictionary
    """

    for key, value in dictionary.items():
        if value == value_to_find:
            return key
    else:
        raise KeyError("Could not find {} in map".format(value_to_find))


@has_log
class EdwardsTICStreamInterface(StreamInterface):

    # Commands that we expect via serial during normal operation
    commands = {
        CmdBuilder("turbo_start_stop").escape("!C904 ").int().eos().build(),
        CmdBuilder("get_turbo_state").escape("?V904").eos().build(),
        CmdBuilder("turbo_get_speed").escape("?V905").eos().build(),
        CmdBuilder("turbo_get_sft").escape("?S905").eos().build(),
        CmdBuilder("turbo_get_power").escape("?V906").eos().build(),
        CmdBuilder("turbo_get_norm").escape("?V907").eos().build(),
        CmdBuilder("turbo_set_standby").escape("!C908 ").int().eos().build(),
        CmdBuilder("turbo_get_standby").escape("?V908").eos().build(),
        CmdBuilder("turbo_get_cycle").escape("?V909").eos().build(),
        CmdBuilder("backing_get_status").escape("?V910").eos().build(),
        CmdBuilder("backing_start_stop").escape("!C910 ").int().eos().build(),
        CmdBuilder("backing_get_speed").escape("?V911").eos().build(),
        CmdBuilder("backing_get_power").escape("?V912").eos().build(),
        CmdBuilder("get_gauge_1").escape("?V913").eos().build(),
        CmdBuilder("get_gauge_2").escape("?V914").eos().build(),
        CmdBuilder("get_gauge_3").escape("?V915").eos().build(),
    }

    in_terminator = "\r"
    out_terminator = "\r"

    ACK = "&ACK!" + out_terminator

    def handle_error(self, request, error):
        """
        Prints an error message if a command is not recognised.

        Args:
            request : Request.
            error: The error that has occurred.
        Returns:
            None.
        """

        self.log.info("An error occurred at request {}: {}".format(request, error))

    @conditional_reply("is_connected")
    def turbo_set_standby(self, switch):
        self._device.turbo_set_standby(switch)

        return "*C908 0"

        #return "=V908 {standby}".format(standby=self._device.turbo_standby)

    def test_get_stby(self):
        # Device replies 0 (off) or 4 (on)
        return "=V908 {};0;0".format()

    @conditional_reply("is_connected")
    def turbo_get_standby(self):
        return_string = "=V908 {stdby_state};0;0"

        #turbo_in_standby = self._device.turbo_standby
        standby_state = 4 if self._device.turbo_in_standby else 0

        self.log.info(return_string.format(stdby_state=standby_state))

        return return_string.format(stdby_state=standby_state)


    @conditional_reply("is_connected")
    def turbo_start_stop(self, switch):
        self.log.info("turbo start stop command received")
        self._device.turbo_start_stop(switch)

        return "*C904 0"

    @conditional_reply("is_connected")
    def get_turbo_state(self):
        state_string = "=V904 {turbo_state};{alert};{priority}"

        return state_string.format(turbo_state=reverse_dict_lookup(PUMPSTATES_MAP, self._device.turbo_pump), 
                                   alert=self._device.turbo_alert,
                                   priority=PRIORITYSTATES_MAP[self._device.turbo_priority])

    @conditional_reply("is_connected")
    def get_turbo_status(self):
        output_string = "*C904 {state};{alert};{priority}"

        state = self._device.turbo_state
        alert = self._device.turbo_alert
        priority = self._device.turbo_priority

        return output_string.format(state=state, alert=alert, priority=priority)

    @conditional_reply("is_connected")
    def turbo_get_speed(self):
        return "=V905 1;0;0"

    @conditional_reply("is_connected")
    def turbo_get_sft(self):
        return "=S905 1;0"

    @conditional_reply("is_connected")
    def turbo_get_power(self):
        return "=V906 1;0;0"

    @conditional_reply("is_connected")
    def turbo_get_norm(self):
        return "=V907 4;0;0"

    @conditional_reply("is_connected")
    def turbo_get_cycle(self):
        return "=V909 1;0;0;0"

    @conditional_reply("is_connected")
    def backing_get_status(self):
        return "=V910 1;0;0"

    @conditional_reply("is_connected")
    def backing_start_stop(self, switch):
        return "*C910 0"

    @conditional_reply("is_connected")
    def backing_get_speed(self):
        return "=V911 1;0;0"

    @conditional_reply("is_connected")
    def backing_get_power(self):
        return "=V912 1;0;0"

    @conditional_reply("is_connected")
    def get_gauge_1(self):
        return "=V913 1;0;0"

    @conditional_reply("is_connected")
    def get_gauge_2(self):
        return "=V914 1;0;0"

    @conditional_reply("is_connected")
    def get_gauge_3(self):
        return "=V915 1;0;0"
