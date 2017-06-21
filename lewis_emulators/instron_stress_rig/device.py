from collections import OrderedDict
from states import DefaultState, GoingToSetpointState
from lewis.devices import StateMachineDevice
from channel import PositionChannel, StrainChannel, StressChannel
from waveform_generator import WaveformGenerator

import time


class SimulatedInstron(StateMachineDevice):

    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """

        # When initialisation is complete, this is set to true and the device will enter a running state
        self.ready = True
        self.control_channel = 1
        self._watchdog_status = (0, 0)
        self._control_mode = 0
        self._actuator_status = 0
        self._movement_type = 2
        self.current_time = 0
        self.watchdog_refresh_time = 0
        self.status = 7680

        # Mode 0 = Ramp waveform
        # Mode 1 = Random waveform
        self._waveform_mode = 0

        # Maps a channel number to a channel object
        self.channels = {1: PositionChannel(), 2: StressChannel(), 3: StrainChannel()}

        self._waveform_generator = WaveformGenerator()

    def raise_exception_if_cannot_write(self):
        if self._control_mode != 1:
            raise Exception("Not in the correct control mode to execute that command!")

    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
            'going': GoingToSetpointState(),
        }

    # This is a workaround for https://github.com/DMSC-Instrument-Data/lewis/issues/248
    def set_channel_param(self, index, param, value):
        setattr(self.channels[int(index)], str(param), value)

    # This is a workaround for https://github.com/DMSC-Instrument-Data/lewis/issues/248
    def get_channel_param(self, index, param):
        return getattr(self.channels[int(index)], str(param))

    # This is a workaround for https://github.com/DMSC-Instrument-Data/lewis/issues/248
    def set_waveform_state(self, value):
        self._waveform_generator.state = value

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([
            (('default', 'going'), lambda: self._movement_type != 0 and self.channels[self.control_channel].value != self.channels[self.control_channel].ramp_amplitude_setpoint),
            (('going', 'default'), lambda: self._movement_type == 0 or self.channels[self.control_channel].value == self.channels[self.control_channel].ramp_amplitude_setpoint),
        ])

    def get_control_channel(self):
        return self.control_channel

    def set_control_channel(self, channel):
        self.control_channel = channel

    def get_watchdog_status(self):
        return self._watchdog_status

    def set_watchdog_status(self, enabled, status):
        self._watchdog_status = (enabled, status)
        self.watchdog_refresh_time = self.current_time

    def get_control_mode(self):
        return self._control_mode

    def set_control_mode(self, mode):
        self._control_mode = mode

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def get_actuator_status(self):
        return self._actuator_status

    def get_status(self):
        return self.status

    def set_actuator_status(self, status):
        self.raise_exception_if_cannot_write()
        self._actuator_status = int(status)
        if status == 0:
            self._movement_type = 0

    def get_movement_type(self):
        return self._movement_type

    def set_movement_type(self, mov_type):
        self.raise_exception_if_cannot_write()

        if self._waveform_mode == 0:
            self._movement_type = mov_type
        else:
            self._movement_type = mov_type + 3

    def set_current_time(self):
        self.current_time = time.time()

    def set_step_time(self, channel, value):
        self.channels[channel].step_time = value

    def get_step_time(self, channel):
        return self.channels[channel].step_time

    def set_chan_waveform_type(self, channel, value):
        self.channels[channel].waveform_type = value

    def get_chan_waveform_type(self, channel):
        return self.channels[channel].waveform_type

    def set_ramp_amplitude_setpoint(self, channel, value):
        self.channels[channel].ramp_amplitude_setpoint = value

    def get_ramp_amplitude_setpoint(self, channel):
        return self.channels[channel].ramp_amplitude_setpoint

    def get_chan_scale(self, channel):
        return self.channels[channel].scale

    def get_chan_value(self, channel, type):
        # Emulator/IOC only currently supports getting current value (type 0).
        # Actual rig accepts values 0-12
        assert int(type) == 0, "Emulator only supports getting current value"
        return self.channels[channel].value

    def get_strain_channel_length(self, channel):
        # Getting the length is only supported for channel 3 (strain).
        assert isinstance(self.channels[channel], StrainChannel), "Length only applies to strain channel"
        # This number gets divided by in the IOC - if it's zero things will break.
        assert self.channels[channel].length != 0, "Strain channel length was zero"
        return self.channels[channel].length

    def get_chan_area(self, channel):
        # Area is only applicable to stress channel
        assert isinstance(self.channels[channel], StressChannel), "Area only applies to stress channel"
        return self.channels[channel].area

    def set_chan_area(self, channel, value):
        # Area is only applicable to stress channel
        assert isinstance(self.channels[channel], StressChannel), "Area only applies to stress channel"
        self.channels[channel].area = value

    def get_chan_type_1(self, channel):
        return self.channels[channel].type_1

    def get_chan_type_2(self, channel):
        return self.channels[channel].type_2

    def get_waveform_status(self):
        return self._waveform_generator.state

    def abort_waveform_generation(self):
        self._waveform_generator.abort()

    def finish_waveform_generation(self):
        self._waveform_generator.finish()

    def start_waveform_generation(self):
        self._waveform_generator.start()

    def stop_waveform_generation_if_requested(self):
        if self._waveform_generator.time_to_stop():
            self._waveform_generator.stop()

    def get_waveform_type(self, channel):
        try:
            return self._waveform_generator.type[channel]
        except NameError:
            print "Unable to get waveform generator type. Channel: {0}".format(channel)

    def set_waveform_type(self, channel, value):
        try:
            self._waveform_generator.type[channel] = value
        except NameError:
            print "Unable to set waveform generator type. Channel: {0}, Value: {1}".format(channel, value)

    def get_waveform_amplitude(self, channel):
        try:
            return self._waveform_generator.amplitude[channel]
        except NameError:
            print "Unable to get waveform generator amplitude. Channel: {0}".format(channel)

    def set_waveform_amplitude(self, channel, value):
        try:
            self._waveform_generator.amplitude[channel] = value
        except NameError:
            print "Unable to set waveform generator amplitude. Channel: {0}, Value: {1}".format(channel, value)

    def get_waveform_frequency(self, channel):
        try:
            return self._waveform_generator.frequency[channel]
        except NameError:
            print "Unable to get waveform generator frequency. Channel: {0}".format(channel)

    def set_waveform_frequency(self, channel, value):
        try:
            self._waveform_generator.frequency[channel] = value
        except NameError:
            print "Unable to set waveform generator frequency. Channel: {0}, Value: {1}".format(channel, value)
