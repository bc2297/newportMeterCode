# This code is property of Apple Inc
# No license is granted unless expressly stated otherwise


import Newport2936R
import time
import pdb
from datetime import datetime

delay_between_commands_sec = 0.1
power_meter_serial_port = "COM9"

# make a pretty printer
def print_results(channel_one, channel_two, delta_time, counter):
    pretty_string_base = "CHAN_ONE:  Val{:.2e} Uni{:d} Ran{:d} Det{:d} Sat{:d} Ring{:d} Over{:d}  " + \
                         "CHAN_TWO:  Val{:.2e} Uni{:d} Ran{:d} Det{:d} Sat{:d} Ring{:d} Over{:d}  " + \
                         "msec:{:d}  cnt:{:d}"
    pretty_filled_in = pretty_string_base.format(channel_one['value'],
                                                 channel_one['units'],
                                                 channel_one['range'],
                                                 channel_one['detector'],
                                                 channel_one['saturated'],
                                                 channel_one['ranging'],
                                                 channel_one['overrange'],
                                                 channel_two['value'],
                                                 channel_two['units'],
                                                 channel_two['range'],
                                                 channel_two['detector'],
                                                 channel_two['saturated'],
                                                 channel_two['ranging'],
                                                 channel_two['overrange'],
                                                 delta_time.microseconds / 1000,
                                                 counter)
    print(pretty_filled_in)

# connect power meter
pm = Newport2936R.Newport2936R(power_meter_serial_port)

# delay after power meter init
time.sleep(1)

#set escape condition
done = False

#get a starting time
this_time = datetime.now()
counter = 0
try:
    while not done:
        counter += 1
        last_time = this_time
        this_time = datetime.now()
        # get time between commands
        delta_time = this_time - last_time
        time.sleep(delay_between_commands_sec)
        try:
            channel_one, channel_two = pm.readPowerAndValidate()
            print_results(channel_one, channel_two, delta_time, counter)
        except Newport2936R.CustomPowerMeterException as e:
            print("Power meter level error:\n{}".format(e))
            print("Breaking program into debugger mode")
            print("pm._serial_ref is direct access to serial port.")
            print("Set done = True and continue to leave loop")
            pdb.set_trace()
except KeyboardInterrupt:
    print("Killed sweep program")
