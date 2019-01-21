from lewis.adapters.modbus import ModbusInterface, ModbusBasicDataBank
from lewis.core.logging import has_log


@has_log
class Moxa1210ModbusInterface(ModbusInterface):
    """
    Creates modbus data registers for a Moxa e1210 and makes them available to the lewis device.
    """

    protocol = "MOXA_1210"

    di = ModbusBasicDataBank(False, last_addr=0x10)
    co = di
    ir = ModbusBasicDataBank(0)
    hr = ir

    @ModbusInterface.device.setter
    def device(self, new_device):
        """
        Overrides base implementation to give attached device a reference to self
        Required to allow communications between the interface and device
        """
        ModbusInterface.device.fset(self, new_device)
        self.device.interface = self

@has_log
class Moxa1240ModbusInterface(ModbusInterface):
    """
    Creates modbus data registers for a Moxa e1240 and makes them available to the lewis device.
    """

    protocol = "MOXA_1240"

    di = ModbusBasicDataBank(False, last_addr=0x10)
    co = di
    ir = ModbusBasicDataBank(10, last_addr=0x80)
    hr = ir

    @ModbusInterface.device.setter
    def device(self, new_device):
        """
        Overrides base implementation to give attached device a reference to self
        Required to allow communications between the interface and device
        """
        ModbusInterface.device.fset(self, new_device)
        self.device.interface = self
