# This code is property of Apple Inc
# No license is granted unless expressly stated otherwise


import serial
import sys
import time

_PY3 = sys.version_info.major == 3


class Newport2936R(object):
    def __init__(self, serial_port):
        self._serial_ref = serial.Serial(serial_port, 38400)
        time.sleep(1)
        try:
            # if meter has ECHO off, first attempt will fail
            self._write_and_read_serial("ECHO 1")
        except:
            self._write_and_read_serial("ECHO 1")

    def __del__(self):
        try:
            self._serial_ref.close()
        except:
            pass

    def readPowerAndValidate(self):
        """Read power and break down components."""
        fullCode = self._write_and_read_serial("PM:PWS?\r")
        splitCode = fullCode.split()
        if len(splitCode) != 4:
            raise ValueError("Returned improper value: {}".format(fullCode))
        channelOne = {}
        channelTwo = {}

        channelOne['value'] = float(splitCode[0])
        channelTwo['value'] = float(splitCode[2])
        # other two values are a bitfield
        # ex: 128 means 0x1 0x2 0x8 or
        # 0001 0010 1000
        # Bits 9-7 Channel Units. See PM:UNITS?
        # Bits 6-4 Channel Range, See PM:RANge?
        # Bit 3 Detector Present
        # Bit 2 Channel range change status. Indicates if a measurement
        # has been taken while the unit is ranging
        # Bit 1 Detector Saturated (reserved, follows bit 0)
        # Bit 0 Channel overrange. Indicates that the current measurement
        # is overrange for the current channel range

        channelOne['units'] = (int(splitCode[1][0], 16) & 0x1) * 2 + (int(splitCode[1][1], 16) & 0x8) / 8
        channelTwo['units'] = (int(splitCode[3][0], 16) & 0x1) * 2 + (int(splitCode[3][1], 16) & 0x8) / 8

        channelOne['range'] = int(splitCode[1][1], 16) & 0x7
        channelTwo['range'] = int(splitCode[3][1], 16) & 0x7

        channelOne['detector'] = bool(int(splitCode[1][2], 16) & 0x8)
        channelTwo['detector'] = bool(int(splitCode[3][2], 16) & 0x8)

        channelOne['ranging'] = bool(int(splitCode[1][2], 16) & 0x4)
        channelTwo['ranging'] = bool(int(splitCode[3][2], 16) & 0x4)

        channelOne['saturated'] = bool(int(splitCode[1][2], 16) & 0x2)
        channelTwo['saturated'] = bool(int(splitCode[3][2], 16) & 0x2)

        channelOne['overrange'] = bool(int(splitCode[1][2], 16) & 0x1)
        channelTwo['overrange'] = bool(int(splitCode[3][2], 16) & 0x1)

        return [channelOne, channelTwo]

    if _PY3:
        def to_unicode(self, bytes_or_str, encoding='utf-8', errors='strict'):
            """Return printable unicode representation of string."""
            return (bytes_or_str.decode(encoding, errors) if isinstance(bytes_or_str, bytes) else
                    bytes_or_str)
    else:
        def to_unicode(self, bytes_or_str, encoding='utf-8', errors='strict'):
            """Return Unicode sequence representing a string."""
            return (bytes_or_str.decode(encoding, errors) if isinstance(bytes_or_str, str) else
                    bytes_or_str)

    if _PY3:
        def to_bytes(self, bytes_or_str, encoding='utf-8', errors='strict'):
            """Return bytes from (unicode) str or bytes."""
            return (bytes_or_str.encode(encoding, errors) if isinstance(bytes_or_str, str)
                    else bytes_or_str)
    else:
        def to_bytes(self, unicode_or_str, encoding='utf-8', errors='strict'):
            """Return bytes from Unicode string or bytes."""
            return (unicode_or_str.encode(encoding, errors) if isinstance(unicode_or_str, unicode) else
                    unicode_or_str)

    def _write_and_read_serial(self, message, timeout_sec=2, end_string="\n"):
        """Method that will write command and read the reply if a query is sent"""
        if not message.endswith("\r"):
            message += "\r"
        self.to_unicode(self._serial_ref.read(self._serial_ref.inWaiting()))
        if '?' in message:
            require_return = True
        else:
            require_return = False
        start_time = time.time()
        self._serial_ref.write(self.to_bytes(message))
        return_string = ""
        while True:
            if time.time() - start_time > timeout_sec:
                raise CustomPowerMeterException("Timeout reading back serial command from message: {}\r\nPartial Return: {}".format(message, return_string))
            if self._serial_ref.inWaiting() != 0:
                return_string += self.to_unicode(self._serial_ref.read(self._serial_ref.inWaiting()))
                if return_string.startswith("{}".format(message)) and len(return_string) > len(message):
                    cropped_return = return_string[len(message):]
                    if cropped_return.endswith(end_string):
                        if not require_return or len(cropped_return) > 1:
                            return_string = cropped_return
                            break
        return return_string.strip()


class CustomPowerMeterException(Exception):
    """Custom Exception class"""

if __name__ == '__main__':
    pm = Newport2936R("COM9")
    channel_one, channel_two = pm.readPowerAndValidate()
