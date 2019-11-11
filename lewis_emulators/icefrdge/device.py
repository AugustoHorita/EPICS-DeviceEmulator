from collections import OrderedDict
from states import DefaultState
from lewis.devices import StateMachineDevice


class VTILoopChannel(object):
    """
    Class to represent an individual channel for controlling loops in the VTI of an ICE dilution fridge. A channel has
    a temperature setpoint, PID values and a ramp rate.
    """

    def __init__(self):
        self.vti_loop_temp_setpoint = 0
        self.vti_loop_proportional = 0
        self.vti_loop_integral = 0
        self.vti_loop_derivative = 0
        self.vti_loop_ramp_rate = 0


class SimulatedIceFridge(StateMachineDevice):

    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """
        self.auto_temp_setpoint = 0
        self.manual_temp_setpoint = 0
        self.vti_temp1 = 0
        self.vti_temp2 = 0
        self.vti_temp3 = 0
        self.vti_temp4 = 0

        self.vti_loop_channels = {
            1: VTILoopChannel(),
            2: VTILoopChannel()
        }

        self.lakeshore_mc_cernox = 0
        self.lakeshore_mc_ruo = 0
        self.lakeshore_still_temp = 0

        self.lakeshore_mc_temp_setpoint = 0
        self.lakeshore_scan = 0
        self.lakeshore_cmode = 0

        self.lakeshore_mc_proportional = 0
        self.lakeshore_mc_integral = 0
        self.lakeshore_mc_derivative = 0

        self.lakeshore_mc_heater_range = 0
        self.lakeshore_mc_heater_percentage = 0
        self.lakeshore_still_output = 0

        self.lakeshore_exc_voltage_range_ch5 = 1
        self.lakeshore_exc_voltage_range_ch6 = 1

        self.mimic_pressures = [0, 0, 0, 0]

    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([
        ])

    def reset(self):
        """
        Public method that re-initializes the device's fields.
        :return: Nothing.
        """
        self._initialize_data()

    def set_mimic_pressure(self, index, new_value):
        """
        Sets a mimic pressure in the mimic pressures list to a new value.
        :param index: the index of the pressure we want to set, from 1 to 4.
        :param new_value: The new pressure value.
        :return: None.
        """
        self.mimic_pressures[index - 1] = new_value
