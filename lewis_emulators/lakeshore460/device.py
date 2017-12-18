from collections import OrderedDict

from lewis.devices import StateMachineDevice
from .states import DefaultState


class SimulatedLakeshore460(StateMachineDevice):
    """
    Simulated AM Int2-L pressure transducer.
    """

    def _initialize_data(self):
        """
        Sets the initial state of the device.
        """
        self._pressure = 2.0
        self.address = "AB"

    def _get_state_handlers(self):
        """
        Returns: states and their names
        """
        return {DefaultState.NAME: DefaultState()}

    def _get_initial_state(self):
        """
        Returns: the name of the initial state
        """
        return DefaultState.NAME

    def _get_transition_handlers(self):
        """
        Returns: the state transitions
        """
        return OrderedDict()

    @property
    def pressure(self):
        """
        Returns: the pressure
        """
        return self._pressure

    @pressure.setter
    def pressure(self, pressure):
        """
        :param pressure: set the pressure
        :return:
        """
        self._pressure = pressure
