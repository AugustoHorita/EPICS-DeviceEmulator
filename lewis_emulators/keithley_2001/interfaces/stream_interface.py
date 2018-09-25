from lewis.adapters.stream import StreamInterface, has_log
from lewis_emulators.utils.command_builder import CmdBuilder

@has_log
class Keithley2001StreamInterface(StreamInterface):

    in_terminator = "\n"
    out_terminator = in_terminator

    commands = {
        CmdBuilder("get_idn").escape("*IDN?").eos().build(),
        CmdBuilder("reset_device").escape("*RST").eos().build(),
        CmdBuilder("clear_buffer").escape(":DATA:CLE").eos().build(),

        CmdBuilder("set_buffer_source").escape(":DATA:FEED ").arg("NONE|SENS1|CALC1").eos().build(),
        CmdBuilder("get_buffer_source").escape(":DATA:FEED?").eos().build(),

        CmdBuilder("set_buffer_mode").escape(":DATA:FEED:CONT ").arg("NEV|NEXT|ALW|PRET").eos().build(),
        CmdBuilder("get_buffer_mode").escape(":DATA:FEED:CONT?").eos().build(),

        CmdBuilder("set_buffer_size").escape(":DATA:POIN ").int().eos().build(),
        CmdBuilder("get_buffer_size").escape(":DATA:POIN?").eos().build(),

        CmdBuilder("get_elements").escape(":FORM:ELEM?").eos().build(),
        CmdBuilder("set_elements").escape(":FORM:ELEM ").string().eos().build()
    }

    def handle_error(self, request, error):
        self.log.error("An error occurred at request {}: {}".format(repr(request), repr(error)))
        print("An error occurred at request {}: {}".format(repr(request), repr(error)))

    def get_idn(self):
        return self._device.idn

    def get_elements(self):
        """
        Returns the lists of elements of a reading in alphabetical order from the device.

        """
        elements = [element for element, value in self._device.elements.items() if value]
        return ", ".join(elements)

    def set_elements(self, string):
        """
        Sets the elements a reading has.

        Args:
            string: String of comma separated elements of a reading. Valid elements are:
                READ, CHAN, RNUM, UNIT, TIME, STAT.
        """
        elements = {element.strip().upper() for element in string.split(",")}

        for element in elements:
            try:
                self._device.elements[element] = True
            except LookupError:
                self.log.error("Tried to set {} which is not a valid reading element.".format(element))
                print("Tried to set {} which is not a valid reading element.".format(element))

    def reset_device(self):
        """
        Resets device.
        """
        self._device.reset_device()

    def clear_buffer(self):
        """
        Clears the buffer.
        """
        self._device.buffer.clear_buffer()

    def set_buffer_source(self, source):
        """
        Sets the buffer source.
        """
        self._device.buffer.source = source

    def get_buffer_source(self):
        """
        Gets the buffer source.
        """
        return self._device.buffer.source

    def set_buffer_mode(self, mode):
        """
        Sets the buffer mode.
        """
        self._device.buffer.mode = mode

    def get_buffer_mode(self):
        """
        Gets the buffer mode.
        """
        return self._device.buffer.mode

    def set_buffer_size(self, size):
        """
        Sets the buffer mode.
        """
        self._device.buffer.size = int(size)

    def get_buffer_size(self):
        """
        Gets the buffer mode.
        """
        return self._device.buffer.size
