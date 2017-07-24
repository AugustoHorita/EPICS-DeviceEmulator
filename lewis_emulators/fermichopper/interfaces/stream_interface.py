from lewis.adapters.stream import StreamAdapter, Cmd


class JulichChecksum(object):
    @staticmethod
    def _hex_value(char):
        """
        Converts an uppercase octadecimal character or a hash to it's ASCII identifier.

        :param char: The character to convert
        :return: the ascii code of the given character
        """
        assert char in list("#0123456789ABCDEFGH"), "Invalid character - can't calculate hex value!"
        return ord(char)

    @staticmethod
    def _calculate(alldata):
        """
        Calculates the Julich checksum of the given data
        :param alldata: the input data (list of chars, length 5)
        :return: the Julich checksum of the given input data
        """
        return "00" if all(x in ['0', '#'] for x in alldata) else hex(sum(JulichChecksum._hex_value(i) for i in alldata)).upper()[-2:]

    @staticmethod
    def verify(header, data, actual_checksum):
        """
        Verifies that the checksum of received data is correct.
        :param header: The leading # and the first byte (str, length 2)
        :param data: The data bytes (str, length 4)
        :param actual_checksum: The transmitted checksum (str, length 2)
        :return: Nothing
        :raises: AssertionError: If the checksum didn't match or the inputs were invalid
        """
        assert len(header) == 2, "Header should have length 2"
        assert len(data) == 4, "Data should have length 4"
        assert len(actual_checksum) == 2, "Actual checksum should have length 2"
        assert JulichChecksum._calculate(list(header) + list(data)) == actual_checksum, "Checksum did not match"

    @staticmethod
    def append_checksum(data):
        """
        Utility method for appending the Julich checksum to the input data
        :param data: the input data
        :return: the input data with it's checksum appended
        """
        assert len(data) == 6, "Unexpected data length."
        return data + JulichChecksum._calculate(data)


class FermichopperStreamInterface(StreamAdapter):

    # Commands that we expect via serial during normal operation
    commands = {
        Cmd("get_all_data", "^#00000([0-9A-F]{2})\$$"),
        Cmd("execute_command", "^#1([0-9A-F]{4})([0-9A-F]{2})\$$"),
        # Cmd("catch_all", "^.*$"), # Catch-all command for debugging
    }

    in_terminator = "\n"
    out_terminator = "\n"

    # Catch all command for debugging if the IOC sends strange characters in the checksum.
    # def catch_all(self):
    #    pass

    def handle_error(self, request, error):
        print "An error occurred at request " + repr(request) + ": " + repr(error)
        return str(error)

    def get_all_data(self, checksum):
        JulichChecksum.verify('#0', '0000', checksum)
        return JulichChecksum.append_checksum('#1' + self._device.get_last_command()) \
                + JulichChecksum.append_checksum("#2003F") \
                + JulichChecksum.append_checksum("#30006") \
                + JulichChecksum.append_checksum("#4464F") \
                + JulichChecksum.append_checksum("#55208") \
                + JulichChecksum.append_checksum("#60000") \
                + JulichChecksum.append_checksum("#75209") \
                + JulichChecksum.append_checksum("#80000") \
                + JulichChecksum.append_checksum("#9002A") \
                + JulichChecksum.append_checksum("#A01EB") \
                + JulichChecksum.append_checksum("#B01F0") \
                + JulichChecksum.append_checksum("#C01F9") \
                + JulichChecksum.append_checksum("#D01FB") \
                + JulichChecksum.append_checksum("#E020C") \
                + JulichChecksum.append_checksum("#F0296") \
                + JulichChecksum.append_checksum("#G0198") \
                + JulichChecksum.append_checksum("#H0176")

    def execute_command(self, command, checksum):
        JulichChecksum.verify('#1', command, checksum)

        valid_commands = ["0001", "0002", "0003", "0006", "0007"]

        assert command in valid_commands, "Invalid command."

        self._device.set_last_command(command)

