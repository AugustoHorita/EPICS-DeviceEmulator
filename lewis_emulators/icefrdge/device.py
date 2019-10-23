from collections import OrderedDict
from states import DefaultState
from lewis.devices import StateMachineDevice


class SimulatedIceFridge(StateMachineDevice):

    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """
        self._auto_temp_setpoint = 0

    @property
    def auto_temp_setpoint(self):
        return self._auto_temp_setpoint

    @auto_temp_setpoint.setter
    def auto_temp_setpoint(self, new_temp_setpoint):
        self._auto_temp_setpoint = new_temp_setpoint

    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([
        ])
