from collections import OrderedDict
from lewis.core.logging import has_log
from states import DefaultState
from lewis.devices import StateMachineDevice


@has_log
class SimulatedWm323(StateMachineDevice):

    def _initialize_data(self):
        """
        Initialize all of the device's attributes.
        """
        self.speed = 0
        self.direction = "CCW"
        self.running = 0

    def _get_state_handlers(self):
        return {'default': DefaultState()}

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([])
