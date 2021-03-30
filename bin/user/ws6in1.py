"""
# Copyright 2020 Bob Atchley
# See the file LICENSE.txt for your full rights.
#

Weatherstations supported (others may need adding)
===============
Youshiko YC9388
Bresser PC 6 in 1
Garni 935PC
Ventus W835

The interface is undocumented.  The following has been determined by
sniffing the usb interface (using Wireshark)

Decoding
========
The hex dump below shows a sequence of data.
These are retrieved in 64 byte chunks (4 lines)

The last byte in each 64 byte sequence is 0xfd
The 2 bytes before this represent a CRC-16/XMODEM checksum of the previous 61
bytes

SECTION 1
The initial section of interest starts with 0xfe00 0000 00xy
x is the number of 64 byte sequences in this section
y is the iteration count
In this example section 1 has 3 64 byte messages hence
where xy is (0x31) then (0x32) then (0x33)
This initial section contains the base output data in ascii space separated
(0x20)

The actual format will change depending on whether '-' or extra
digits are needed

00000100: fe00 0000 0031 3635 2032 3032 302d 3031  .....165 2020-01
00000110: 2d31 3920 3138 3a35 3720 3234 2e35 2034  -19 18:57 24.5 4
00000120: 3120 2d30 2e32 2039 3720 302e 3020 302e  1 -0.2 97 0.0 0.
00000130: 3020 302e 3020 302e 3020 3333 33b0 0bfd  0 0.0 0.0 333...

00000140: fe00 0000 0032 3620 4e4e 5720 3130 3431  .....26 NNW 1041
00000150: 2031 3034 3020 3020 2d30 2e36 202d 2d2e   1040 0 -0.6 --.
00000160: 2d20 2d2d 2e2d 202d 2d20 2d2d 2e2d 202d  - --.- -- --.- -
00000170: 2d20 2d2d 2e2d 202d 2d20 2d2d 2e56 f8fd  - --.- -- --.V..

00000180: fe00 0000 0033 1c2d 202d 2d20 2d2d 2e2d  .....3.- -- --.-
00000190: 202d 2d20 2d2d 2e2d 202d 2d20 2d2d 2e2d   -- --.- -- --.-
000001a0: 202d 2d00 0000 0000 0000 0000 0000 0000   --.............
000001b0: 0000 0000 0000 0000 0000 0000 0061 e8fd  .............a..

SECTION 2
This next section provides similar information but spelt out in Ascii
Each 64 byte starts with 0xfb00 0000 00xy
In this example section 2 has 4 64 byte messages hence
where xy is (0x41) then (0x42) then (0x43) then (0x44)

000001c0: fb00 0000 0041 3626 6461 7465 7574 633d  .....A6&dateutc=
000001d0: 6e6f 7726 6261 726f 6d69 6e3d 3330 2e37  now&baromin=30.7
000001e0: 3426 7465 6d70 663d 3331 2e36 2668 756d  4&tempf=31.6&hum
000001f0: 6964 6974 793d 3937 2677 696e 6436 43fd  idity=97&wind6C.

00000200: fb00 0000 0042 3673 7065 6564 6d70 683d  .....B6speedmph=
00000210: 3026 7769 6e64 6775 7374 6d70 683d 3026  0&windgustmph=0&
00000220: 7769 6e64 6469 723d 3333 3326 6465 7770  winddir=333&dewp
00000230: 7466 3d33 302e 3926 7261 696e 691a 45fd  tf=30.9&raini.E.

00000240: fb00 0000 0043 366e 3d30 2664 6169 6c79  .....C6n=0&daily
00000250: 7261 696e 696e 3d30 2655 563d 3026 696e  rainin=0&UV=0&in
00000260: 646f 6f72 7465 6d70 663d 3736 2e31 2669  doortempf=76.1&i
00000270: 6e64 6f6f 7268 756d 6964 6974 7919 0efd  ndoorhumidity...

00000280: fb00 0000 0044 033d 3431 0000 0000 0000  .....D.=41......
00000290: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000002a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000002b0: 0000 0000 0000 0000 0000 0000 005e 1afd  .............^..

SECTION 3
This next section provides more information again spelt out in Ascii
Each 64 byte starts with 0xf100 0000 00xy
In this example section 3 has 3 64 byte messages hence
where xy is (0x31) then (0x32) then (0x33)

This section is usually not present

000002c0: f100 0000 0031 362f 6261 722f 3130 3431  .....16/bar/1041
000002d0: 302f 7764 6972 2f33 3333 2f77 7370 642f  0/wdir/333/wspd/
000002e0: 302f 7773 7064 6869 2f30 2f72 6169 6e72  0/wspdhi/0/rainr
000002f0: 6174 652f 302f 7261 696e 2f30 2fc9 d5fd  ate/0/rain/0/...

00000300: f100 0000 0032 3675 7669 2f30 2f74 656d  .....26uvi/0/tem
00000310: 702f 2d32 2f68 756d 2f39 372f 6465 772f  p/-2/hum/97/dew/
00000320: 2d36 2f63 6869 6c6c 2f2d 322f 7465 6d70  -6/chill/-2/temp
00000330: 696e 2f32 3435 2f68 756d 696e 2f50 5afd  in/245/humin/PZ.

00000340: f100 0000 0033 0234 3100 0000 0000 0000  .....3.41.......
00000350: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000360: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000370: 0000 0000 0000 0000 0000 0000 00ff c9fd  ................

SECTION 4
This next section is essentially an empty buffer with no useful information
Each 64 byte starts with 0xfa03 0000 0000 - these can be discarded

00000380: fa03 0000 0000 0000 0000 0000 0000 0000  ................
00000390: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000003a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000003b0: 0000 0000 0000 0000 0000 0000 00ec 85fd  ................

000003c0: fa03 0000 0000 0000 0000 0000 0000 0000  ................
000003d0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000003e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000003f0: 0000 0000 0000 0000 0000 0000 00ec 85fd  ................

After this the sequence repeats

Other Sequences.  It is possible to request the history of recorded
data from the console.
Some notes on this:
1) period is set at the console only.  Default 30 mins
2) The only way to clear the data is at the console.
3) when the history data buffer is full no more data is written until
   the data buffer is manually cleared

History:
-------
When the history data is downloaded this is done in an identical way
to Section 1 except:

 fe 0000 0000 is replaced.

The first 2 bytes after the 'fe' are the total number of data history items
The second 2 bytes is the count of bytes so

fe 0100 001a

would mean that their are a total of 256 data items (0x0100) and the current
retrieved data item is the 26th (0x001a)

The data items are retrieved in count and chronological order

Note: if the data log has been cleared on the console then the following
data will be retured:

fe ffff ffff 11

After this the buffer is filled with 0's and the correct CRC FD given

===============================

Break down of section 1
00000100:                3635 2032 3032 302d 3031  .....165 2020-01
00000110: 2d31 3920 3138 3a35 3720 3234 2e35 2034  -19 18:57 24.5 4
00000120: 3120 2d30 2e32 2039 3720 302e 3020 302e  1 -0.2 97 0.0 0.
00000130: 3020 302e 3020 302e 3020 3333 33         0 0.0 0.0 333...

00000140:                3620 4e4e 5720 3130 3431  .....26 NNW 1041
00000150: 2031 3034 3020 3020 2d30 2e36 202d 2d2e   1040 0 -0.6 --.
00000160: 2d20 2d2d 2e2d 202d 2d20 2d2d 2e2d 202d  - --.- -- --.- -
00000170: 2d20 2d2d 2e2d 202d 2d20 2d2d 2e         - --.- -- --.V..

00000180:                1c2d 202d 2d20 2d2d 2e2d  .....3.- -- --.-
00000190: 202d 2d20 2d2d 2e2d 202d 2d20 2d2d 2e2d   -- --.- -- --.-
000001a0: 202d 2d00 0000 0000 0000 0000 0000 0000   --.............
000001b0: 0000 0000 0000 0000 0000 0000 00         .............a..

0x3635 (65) : unknown meaning
0x20 (space)
0x3032302d30312d3139 (2020-01-19) the date "yyyy-mm-dd"
0x20 (space)
0x383a3537 (18:57) the time "HH:MM"
0x20 (space)
0x32342e35 (24.5) indoor temp in deg C
0x20 (space)
0x3431 (41) indoor Humidity %
0x20 (space)
0x302e32 (-0.2) outdoor temp in deg C
0x20 (space)
0x3937 (97) outdoor humidity %
0x20 (space)
0x302e30 (0.0) Rain Daily (from midnight) in mm
0x20 (space)
0x302e30 (0.0) Rain Hour in mm
0x20 (space)
0x302e30 (0.0) wind speed km/h
0x20 (space)
0x302e30 (0.0) wind gust km/h
0x20 (space)
0x333333 (333) Wind direction degrees
0x36 (6) unknown
0x20 (space)
0x4e4e57 (NNW) Wind direction
0x20 (space)
0x31303431 (1041) Barometer -Relative (HPa)
0x20 (space)
0x31303430 (1040) Barometer -Absolute (HPa)
0x20 (space)
0x30 (0) UV index ?
0x20 (space)
0x2d302e36 (-0.6) Dewpoint deg C
0x20 (space)
After this there are settings probably for the extra sensors
0x2d2d2e2d 0x20 (--.- )  not sure ?
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 1 temp and humidity
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 2 temp and humidity
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 3 temp and humidity
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 4 temp and humidity
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 5 temp and humidity
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 6 temp and humidity
0x2d2d2e2d 0x20 0x2d2d 0x20 (--.- -- ) channel 7 temp and humidity
Remaining section 1 filled with 0x00

===============================

Break down of section 2

000001c0:                3626 6461 7465 7574 633d  .....A6&dateutc=
000001d0: 6e6f 7726 6261 726f 6d69 6e3d 3330 2e37  now&baromin=30.7
000001e0: 3426 7465 6d70 663d 3331 2e36 2668 756d  4&tempf=31.6&hum
000001f0: 6964 6974 793d 3937 2677 696e 64         idity=97&wind6C.

00000200:                3673 7065 6564 6d70 683d  .....B6speedmph=
00000210: 3026 7769 6e64 6775 7374 6d70 683d 3026  0&windgustmph=0&
00000220: 7769 6e64 6469 723d 3333 3326 6465 7770  winddir=333&dewp
00000230: 7466 3d33 302e 3926 7261 696e 69         tf=30.9&raini.E.

00000240:                366e 3d30 2664 6169 6c79  .....C6n=0&daily
00000250: 7261 696e 696e 3d30 2655 563d 3026 696e  rainin=0&UV=0&in
00000260: 646f 6f72 7465 6d70 663d 3736 2e31 2669  doortempf=76.1&i
00000270: 6e64 6f6f 7268 756d 6964 6974 79         ndoorhumidity...

00000280:                033d 3431 0000 0000 0000  .....D.=41......
00000290: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000002a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000002b0: 0000 0000 0000 0000 0000 0000 00         .............^..

0x36 (A) unknown
0x26 (&) separator
0x6174657574633d6e6f77 dateutc=now
0x26 (&) separator
0x6261726f6d696e3d33302e3734 baromin=30.74
0x26 (&) separator
0x74656d70663d33312e36 tempf=31.6
0x26 (&) separator
0x68756d69646974793d3937 humidity=97
0x26 (&) separator
0x77696e6473706565646d70683d30 windspeedmph=0 - note ignores 0x36 at start
0x26 (&) separator
0x77696e64677573746d70683d30 windgustmph=0
0x26 (&) separator
0x77696e646469723d333333 winddir=333
0x26 (&) separator
0x6465777074663d33302e39 dewptf=30.9
0x26 (&) separator
0x7261696e696e3d30 rainin=0  - note ignores 0x36 at start
0x26 (&) separator
0x6461696c797261696e696e3d30 dailyrainin=0
0x26 (&) separator
0x55563d30 UV=0
0x26 (&) separator
0x696e646f6f7274656d70663d37362e31 indoortempf=76.1
0x26 (&) separator
0x696e646f6f7268756d69646974793d3431 indoorhumidity=41 - note ignores 0x03 at start

Filled with zeros to end

===============================

Break down of section 3

000002c0:                362f 6261 722f 3130 3431  .....16/bar/1041
000002d0: 302f 7764 6972 2f33 3333 2f77 7370 642f  0/wdir/333/wspd/
000002e0: 302f 7773 7064 6869 2f30 2f72 6169 6e72  0/wspdhi/0/rainr
000002f0: 6174 652f 302f 7261 696e 2f30 2f         ate/0/rain/0/...

00000300:                3675 7669 2f30 2f74 656d  .....26uvi/0/tem
00000310: 702f 2d32 2f68 756d 2f39 372f 6465 772f  p/-2/hum/97/dew/
00000320: 2d36 2f63 6869 6c6c 2f2d 322f 7465 6d70  -6/chill/-2/temp
00000330: 696e 2f32 3435 2f68 756d 696e 2f         in/245/humin/PZ.

00000340:                0234 3100 0000 0000 0000  .....3.41.......
00000350: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000360: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000370: 0000 0000 0000 0000 0000 0000 00         ................

0x36 (6) unknown
0x2f (/) Separator
0x61722f3130343130 bar/10410
0x2f (/) Separator
0x6469722f333333 wdir/333
0x2f (/) Separator
0x777370642f30 wspd/0
0x2f (/) Separator
0x7773706468692f30 wspdhi/0
0x2f (/) Separator
0x7261696e726174652f30 rainrate/0
0x2f (/) Separator
0x7261696e2f30 rain/0
0x2f (/) Separator
0x7576692f30 uvi/0
0x2f (/) Separator
0x74656d702f2d32 temp/-2
0x2f (/) Separator
0x68756d2f3937 hum/97
0x2f (/) Separator
0x6465772f2d36 dew/-6
0x2f (/) Separator
0x6368696c6c2f2d32 chill/-2
0x2f (/) Separator
0x74656d70696e2f323435 tempin/245
0x2f (/) Separator
0x68756d696e2f3431 humin/41

Initial decode will only look at section 1 - all other blocks discarded

==============
Additional:

From the provided Youshiko Windows software commands are sent to the console.
These are 8 bytes in length.
The first byte is always 0xfc.
The last byte is always 0xfd
The penultimate 2 bytes are the check sum (CRC-16/xmodem) of the first
5 bytes As some of the commands have the check sum bytes the wrong way
around I'm not convinced the console actually checks the checksum.
These are the values I have seen

0xfc07000000e550fd : first command
0xfc030000002fa1fd : 2nd command - seen a few times (update now)
0xfcd4010000e1bffd : repeated many times
0xfc08140107cbedfd : seen once, crc checksum wrong way around
0xfc09141b0d8dd6fd : seen once, crc checksum wrong way around
0xfcd5010000970bfd : seen many times
0xfcd4020000b8effd : seen a few times
0xfc050000000838fd : seen once before history dump

I don't know for sure what any of these mean and of course their may
be other commands that I haven't seen

The console is keen to provide data as long as something is sent.
With the Youshiko software the 7+ 64 byte
chunks are sent quickly with a 12 second delay until the next set,
but I just seem to get regular spread out dumps (but 12 second cycle)

Guesses at command sequences (all these may be wrong and/or incomplete)
0x0700: initialisation
0x0300: provide latest reading now
0xd401: Ack and continue
0xd501: Ack and continue
0xd402: ? Possibly a Nack ?
0x0500: Request history dump (confirmed working)
0x08: date (yy mm dd in hex)
0x09: time (hh mm ss in hex)

I'm guessing the 2 command sequences with erroneous CRC check sums are
code defects (but this may be completely wrong).  These seem to give date/time

I have no idea what the difference between 0xd401 and 0xd501.

If a sleep is used the Ack and continue retrieves the now stale data.

"""
###############################################################################

import struct
import time
import logging
from datetime import datetime
import crcmod
import usb.core
import usb.util

import weewx.drivers

log = logging.getLogger(__name__)

DRIVER_NAME = 'WS6in1'
DRIVER_VERSION = "1.03"

#------------------------------------------------------------------------------
# loader
#------------------------------------------------------------------------------
# Required weewx driver function to return the instance of the ws6in1 driver
#
# config_dict: the configuration dictionary
# engine:      a reference to the weewx engine
#------------------------------------------------------------------------------
def loader(config_dict, engine):
    """returns the ws6in1 driver instance"""
    return ws6in1(**config_dict[DRIVER_NAME])
# end def loader

###############################################################################
# Class ws6in1
###############################################################################
# Main class for defining the interface between the WS 6 in 1 weather stations
# and weewx
#
# Inherits from weewx.drivers.AbstractDevice
###############################################################################
class ws6in1(weewx.drivers.AbstractDevice):
    """ws6in1 is the main driver class for use with weewx and WS6in1 compatible
    weather station consoles"""

    #-------------------------------------------------------
    # Constructor
    #
    # stn_dict contains the input parameters - the only expected one is the model
    # the default is WS6in1
    #-------------------------------------------------------
    def __init__(self, **stn_dict):

        # get data from the configuration if available
        self.model = stn_dict.get('model', 'WS6in1')
        ws_type = stn_dict.get('wsType', 'WS6in1')
        ws_type = ws_type.upper()
        self.uv_flag = True
        if ws_type == "WS5IN1":
            self.uv_flag = False

        # initialise other parameters
        self.initialised = False
        self.index = 0
        self.vendor = 0x1941
        self.product = 0x8021
        self.last_rain = None
        self.ws_status = 0
        self.bad_values = 0
        self.time_set = False
        self.last_time_set = time.time()
        self.use_archive_time = False
        self.last_ts = 0

        self.my_cfg = None
        self.buff = None
        self.dev = None
        self.in1 = None
        self.in2 = None
        self.in3 = None
        self.in4 = None

        log.info("driver version is %s, Model is %s, Type is %s", DRIVER_VERSION, self.model, ws_type)
    # end __init__

    #--------------------------------------------------------------------------
    # archive_interval
    #--------------------------------------------------------------------------
    # provides the archive interval in seconds
    # As genArchiveRecords cannot be implemented it' better not to implement
    # this.  Instead the weewx engine will use the value specified in
    # [StdArchive] section of the weewx.conf file.
    #--------------------------------------------------------------------------
    #@property
    #def archive_interval(self):
    # end archive_interval

    #--------------------------------------------------------------------------
    # hardware_name
    #--------------------------------------------------------------------------
    # Unfortunately there is no provision to obtain the model from the station
    # itself, so use what is specified from the configuration file.
    #--------------------------------------------------------------------------
    @property
    def hardware_name(self):
        """Provides the hardware name of the weather station"""
        return self.model

    #-------------------------------------------------------
    # get_float
    #-------------------------------------------------------
    # Part of the decode sequence this looks at the next part
    # of the buffer and interprets it as a float.
    #
    # needs more error checking ...
    #
    #-------------------------------------------------------
    def get_float(self):
        """Decodes input data to float"""

        my_str = ""
        end = False

        while self.index + 1 < len(self.buff) and not end:
            my_char = str(chr(self.buff[self.index]))
            my_str = my_str + str(my_char)
            self.index = self.index + 1
            if self.buff[self.index] == 0x20:
                self.index = self.index+1
                end = True
        if my_str == "--.-":
            return None

        try:
            retval = float(my_str)
        except ValueError as my_error:
            log.error("get_float::ValueError error: %s  string: %s", my_error, my_str)
            retval = None
            self.bad_values = self.bad_values + 1

        return retval

    # end def get_float

    #-------------------------------------------------------
    # get_int
    #-------------------------------------------------------
    # Part of the decode sequence this looks at the next part
    # of the buffer and interprets it as an integer.
    #
    # needs more error checking ...
    #
    #-------------------------------------------------------
    def get_int(self):
        """Decodes input data to int"""

        my_str = ""
        end = False

        while self.index + 1 < len(self.buff) and not end:
            my_char = str(chr(self.buff[self.index]))
            my_str = my_str + str(my_char)
            self.index = self.index + 1
            if self.buff[self.index] == 0x20 or self.buff[self.index] == 0x00:
                self.index = self.index+1
                end = True
        if my_str == "--" or my_str == "---":
            return None

        try:
            retval = int(my_str)
        except ValueError as my_error:
            log.error("get_int::ValueError error: %s  string: %s", my_error, my_str)
            retval = None
            self.bad_values = self.bad_values + 1

        return retval

    # end def get_int

    #-------------------------------------------------------
    # get_string
    #-------------------------------------------------------
    # Part of the decode sequence this looks at the next part
    # of the buffer and interprets it as a string.
    #-------------------------------------------------------
    def get_string(self):
        """Decodes input data to string"""

        my_str = ""
        end = False

        while self.index + 1 < len(self.buff) and not end:
            my_char = str(chr(self.buff[self.index]))
            my_str = my_str + str(my_char)
            self.index = self.index + 1
            if self.buff[self.index] == 0x20:
                self.index = self.index+1
                end = True

        return my_str

    # end def get_string

    #--------------------------------------------------------------------------
    # get_archive_epoch
    #--------------------------------------------------------------------------
    # calculates the time in seconds since the epoch for the archive time
    #--------------------------------------------------------------------------
    # ws_date gives the archive date expected format is YYYY-MM-DD
    # ws_time gives the archive time expected format is HH-MM
    #--------------------------------------------------------------------------
    def get_archive_epoch(self, ws_date, ws_time):
        """Converts the date time from the console to a unix epoch time"""

        try:
            date_time = ws_date + ' ' + ws_time + ':00'			
            pattern = '%Y-%m-%d %H:%M:%S'			
            my_epoch = int(time.mktime(time.strptime(date_time, pattern)))

        except ValueError as my_error:
            log.error("get_archive_epoch::ValueError error: %s  date: %s  time: %s",
                      my_error, ws_date, ws_time)
            my_epoch = None
            self.bad_values = self.bad_values + 1

        return my_epoch

    # end get_archive_epoch

    #-------------------------------------------------------
    # rain_delta
    #-------------------------------------------------------
    # works out the rain delta from the previous reading
    #
    # rain_in is the current rain reading (from midnight)
    #-------------------------------------------------------
    def rain_delta(self, rain_in):
        """determines the rain from the last reading and current"""

        # The default is no rain delta.  Only need to check this if
        # last_rain is valid and different to rain_in - otherwise 0.0
        rain_diff = 0.0

        if self.last_rain is not None:

            if rain_in > self.last_rain:
                rain_diff = rain_in - self.last_rain
            elif rain_in < self.last_rain:
                # 2 possibilies either mid night has passed so rain reset
                # or the station has hiccupped.
                # Assume the station never hiccups for the moment ...
                rain_diff = rain_in
        self.last_rain = rain_in
        return rain_diff

    # end def rain_delta

    #-------------------------------------------------------
    # decode
    #-------------------------------------------------------
    # This is the main decode sequence
    # it interprets the buffer input read from the weather
    # station and interprets it into a sequence of values
    #
    # level is the number of 64 byte messages received
    #-------------------------------------------------------
    def decode(self, level):
        """Main decoder - takes the input data buffer and determines the
        individual values"""

        self.ws_status = 0
        self.bad_values = 0

        # weewx packet to be returned
        packet = {}

        # step 1 join the parts together
        j = 0
        i = 0
        self.buff = bytearray()
        tmp = bytearray()

        #lots can go wrong in the decode .. if it does lets skip
        try:

            # loop for j = 1 to level
            j = 1
            while j <= level:
                if j == 1:
                    tmp = bytearray(self.in1)
                elif j == 2:
                    tmp = bytearray(self.in2)
                elif j == 3:
                    tmp = bytearray(self.in3)
                elif j == 4:
                    tmp = bytearray(self.in4)
                else:
                    # error shouldn't get here
                    log.error("decode: unexpected level=%d", j)

                # construct the buffer
                j = j + 1
                k = 7
                while k < 61:
                    self.buff.append(tmp[k])
                    i = i + 1
                    k = k + 1
                    if j > level and tmp[k] == 0x00:
                        self.buff.append(0x20) # end with a space
                        k = 64

            # buff should contain the ascii values that are needed
            self.index = 0

            # get an integer - we throw this away
            self.get_int()

            ws_date = self.get_string()

            ws_time = self.get_string()

            in_temp = self.get_float()

            in_humid = self.get_int()

            out_temp = self.get_float()

            out_humid = self.get_int()

            rain_day = self.get_float()
            rain_rate = self.get_float()

            wind_speed = self.get_float()

            wind_gust = self.get_float()

            wind_dir_deg = self.get_int()

            # wind_dir_str =
            self.get_string()

            barom_rel = self.get_int()

            barom_abs = self.get_int()

            uv_index = self.get_int()

            dewpoint = self.get_float()

            heatindex = self.get_float()

            ## get the 7 temp/humidity sensor data
            extra_temp1 = self.get_float()
            extra_humid1 = self.get_int()
            extra_temp2 = self.get_float()
            extra_humid2 = self.get_int()
            extra_temp3 = self.get_float()
            extra_humid3 = self.get_int()
            extra_temp4 = self.get_float()
            extra_humid4 = self.get_int()
            extra_temp5 = self.get_float()
            extra_humid5 = self.get_int()
            extra_temp6 = self.get_float()
            extra_humid6 = self.get_int()
            extra_temp7 = self.get_float()
            extra_humid7 = self.get_int()

            my_interval = 0
            if self.use_archive_time:
                log.debug("decode::gettint time")
                my_time = self.get_archive_epoch(ws_date, ws_time)

                if my_time != None:

                    # protect against last_ts being None (can happen for empty database)
                    if self.last_ts != None:
                        my_interval = my_time - self.last_ts
                        if my_interval < 0:
                            my_interval = 0

                    self.last_ts = my_time

            else:
                # weewx time - use local time as its accurate (ntp, utc)
                my_time = int(time.time() + 0.5)

            # weewx uses packet ...
            packet['usUnits'] = weewx.METRIC
            packet['dateTime'] = my_time
            log.debug("decode::got my_time: %d", my_time)
            packet['inTemp'] = in_temp
            packet['inHumidity'] = in_humid
            packet['outTemp'] = out_temp
            packet['outHumidity'] = out_humid
            packet['dayRain'] = rain_day * 0.1 # convert to cm
            packet['rainRate'] = rain_rate * 0.1 # convert to cm   
            packet['rain'] = self.rain_delta(rain_day) * 0.1 # convert to cm
            packet['windSpeed'] = wind_speed
            packet['windGust'] = wind_gust
            packet['windDir'] = wind_dir_deg
            packet['pressure'] = barom_abs
            packet['barometer'] = barom_rel
            if self.uv_flag:
                packet['UV'] = uv_index
            packet['dewpoint'] = dewpoint
            packet['heatindex'] = heatindex
            packet['extraHumid1'] = extra_humid1
            packet['extraHumid2'] = extra_humid2
            packet['extraHumid3'] = extra_humid3
            packet['extraHumid4'] = extra_humid4
            packet['extraHumid5'] = extra_humid5
            packet['extraHumid6'] = extra_humid6
            packet['extraHumid7'] = extra_humid7
            packet['extraTemp1'] = extra_temp1
            packet['extraTemp2'] = extra_temp2
            packet['extraTemp3'] = extra_temp3
            packet['extraTemp4'] = extra_temp4
            packet['extraTemp5'] = extra_temp5
            packet['extraTemp6'] = extra_temp6
            packet['extraTemp7'] = extra_temp7
            self.ws_status = 1

            if self.use_archive_time:
                if my_time is None:
                    self.ws_status = 0
                    log.warning("decode:: bad Archive Time - archive record not recoverable")
                else:
                    packet['interval'] = my_interval

            if self.bad_values > 0:
                log.warning("decode: %d bad values occurred - rejecting this set of readings",
                            self.bad_values)
                print("buflen=" + str(len(self.buff)) + "  level=" + str(level))
                for i in range(len(self.buff)):
                    print(str(self.buff[i]) + " ")
                print("int1:")
                for i in range(len(self.in1)):
                    print(str(self.in1[i]) + " ")

                # bad_values occurring in the start records: wrorong time and
                # missing values means it is better to reject this set of data
                # reading rather than try and process them (version 0.6 tried
                # to continue)
                self.ws_status = 0

        except IOError as my_error:
            log.error("decode::IOError error: %s", my_error)
            self.ws_status = 0

        except ValueError as my_error:
            log.error("decode::ValueError error: %s", my_error)
            print("buflen="+str(len(self.buff))+"  level=" + str(level))
            for i in range(len(self.buff)):
                print(str(self.buff[i]) + " ")
            print("int1:")
            for i in range(len(self.in1)):
                print(str(self.in1[i])+" ")
            self.ws_status = 0

        return packet

    #end def decode

    #-------------------------------------------------------
    # find our device
    #-------------------------------------------------------
    # Expect to find the 6 in 1 (+7).  Not finding it is a
    # show stopper
    #-------------------------------------------------------
    def find_my_device(self):
        """Gets the usb device from the vendor attributes"""

        self.dev = usb.core.find(idVendor=self.vendor, idProduct=self.product)

        if self.dev is None:
            log.critical("find_my_device: dev not found")
            raise ValueError('Device not found')

        # check if kernel driver
        log.info("find_my_device::success getting dev")

    # end find_my_device

    #-------------------------------------------------------
    # initialise_my_device
    #-------------------------------------------------------
    # Various commands that initialise the weather station
    # before the main loop is initiated
    #-------------------------------------------------------
    def initialise_my_device(self):
        """Initialises the usb connection for communication with the console"""

        # check if the kernel has it ...
        if self.dev.is_kernel_driver_active(0):
            log.debug("initialise_my_device::need to detach from the kernel")
            self.dev.detach_kernel_driver(0)
            log.debug("initialise_my_device::detached")

        # reset the device
        self.dev.reset()

        # dev is known ... log some parameters
        log.debug("initialise_my_device::dev.bLength            = %s", self.dev.bLength)
        log.debug("initialise_my_device::dev.bNumConfigurations = %s", self.dev.bNumConfigurations)
        log.debug("initialise_my_device::dev.bDeviceClass       = %s", self.dev.bDeviceClass)

        # get the active configuration
        self.my_cfg = self.dev.get_active_configuration()

        if self.my_cfg is None:
            log.error("initialise_my_device: cfg not found")
            raise ValueError('configuration not found')

        # cfg is known ... log some parameters
        log.info("initialise_my_device::success getting configuration")
        log.info("initialise_my_device::my_cfg.bConfigurationValue = %s",
                 self.my_cfg.bConfigurationValue)
        log.info("initialise_my_device::my_cfg.bNumInterfaces      = %s\n",
                 self.my_cfg.bNumInterfaces)

        # set parameters
        usb_request_type = 0x0a
        wlength = 0

        # set to idle
        try:
            #retval =
            self.dev.ctrl_transfer(
                0x21,              # USB Request Type
                usb_request_type,  # USB Request
                wlength)           # WValue

            log.debug("initialise_my_device::Set idle done")

        except ValueError:
            log.info("initialise_my_device::Exception setting idle (this is ok)")

        self.initialised = True

        # set parameters
        usb_request = 0x09
        wvalue = 0x0200
        timeout = 30000  # Milliseconds
        start_buf = struct.pack('BBBBBBBB',
                                0xFC,
                                0x07,
                                0x00,
                                0x00,
                                0x00,
                                0xE5,
                                0x50,
                                0xFD)

        try:
            self.dev.ctrl_transfer(
                0x21,         # USB Request Type
                usb_request,  # USB Request
                wvalue,       # WValue
                0,            # Index
                start_buf,    # Message
                timeout)

            #out=
            self.dev.read(0x81, 64, timeout)
            # not processing the initiatisation read ...
        except ValueError:
            log.error("initialise_my_device::initialisation start failed")

    # end dev initialise_my_device


    #---------------------------------------------------------------
    # genLoopPackets
    #---------------------------------------------------------------
    # this is the main loop that sends commands and reads responses
    # it calls decode to write the output
    #---------------------------------------------------------------
    def genLoopPackets(self):
        """Main function that gets current data from the console and calls decode to
        decode it.  Results are 'yielded' to the weewx engine"""

        self.use_archive_time = False
        tcount = 0
        self.ws_status = 0

        log.debug("genLoopPackets: starting read loop ...")

        if not self.initialised:
            self.find_my_device()
            self.initialise_my_device()

        # set parameters
        usb_request = 0x09
        wvalue = 0x0200
        timeout = 30000  # Milliseconds 30 seconds
        decode_ok = False

        # create function from crcmod to check CRCs
        crcfunc = crcmod.predefined.mkCrcFun('xmodem')

        # Construct known binary messages

        ack2_buf = struct.pack('BBBBBBBB',
                               0xFC,
                               0xD5,
                               0x01,
                               0x00,
                               0x00,
                               0x97,
                               0x0B,
                               0xFD)

        #ack1_buf = struct.pack('BBBBBBBB',
        #                       0xFC,
        #                       0xD4,
        #                       0x01,
        #                       0x00,
        #                       0x00,
        #                       0xE1,
        #                       0xBF,
        #                       0xFD)

        now_buf = struct.pack('BBBBBBBB',
                              0xFC,
                              0x03,
                              0x00,
                              0x00,
                              0x00,
                              0x2F,
                              0xA1,
                              0xFD)

        # do some looping
        packet = {}
        packet['usUnits'] = weewx.METRIC

        count = 0
        while True:
            count += 1

            # buf is the command passed to the console
            # if sleep is being used the 'now_buf' gets the latest
            # if sleep is not being used the 'ack2_buf' works well
            buf = ack2_buf
            if count == 1:
                buf = now_buf

            try:
                #retval =
                self.dev.ctrl_transfer(
                    0x21,         # USB Request Type
                    usb_request,  # USB Request
                    wvalue,       # WValue
                    0,            # Index
                    buf,          # Message
                    timeout)

                out = self.dev.read(0x81, 64, timeout)

                # check to see if this is of interest
                loc_a = out[0]
                #b = out[1]
                loc_c = out[5]
                loc_d = out[63]

                if loc_a == 0xfe:
                    crc_ok = True
                    crc_a = crcfunc(out[0:63])
                    if loc_d != 0xfd or crc_a != 0:
                        crc_ok = False
                        decode_ok = False
                        log.warning("genLoopPackets: bad CRC")

                    if (loc_c == 0x11 or loc_c == 0x21 or loc_c == 0x31 or
                            loc_c == 0x41) and crc_ok:
                        self.in1 = bytearray(out)
                        decode_ok = True

                        if loc_c == 0x11:
                            level = 1
                            packet = self.decode(level)

                    elif (loc_c == 0x22 or loc_c == 0x32 or loc_c == 0x42) and decode_ok:
                        self.in2 = bytearray(out)

                        if loc_c == 0x22:
                            level = 2
                            packet = self.decode(level)

                    elif (loc_c == 0x33 or loc_c == 0x43) and decode_ok:
                        self.in3 = bytearray(out)

                        if loc_c == 0x33:
                            level = 3
                            packet = self.decode(level)

                    elif loc_c == 0x44 and decode_ok:
                        self.in4 = bytearray(out)
                        level = 4
                        packet = self.decode(level)

                    elif not decode_ok:
                        pass
                    else:
                        log.debug("genLoopPackets::unexpected value of c=%s", str(loc_c))

            # the exits below are good for the beta, better as pass
            # for issued version (and most not needed)
            except IOError as my_error:
                log.error("genLoopPackets::IOError error: %s", my_error)
                # the most likely explanation is a timeout
                tcount = tcount + 1
                count = 0
                if tcount > 5:
                    log.critical("genLoopPackets::IOError critical (too many timeouts): %s",
                                 my_error)
                    exit()
                try:
                    out = self.dev.read(0x81, 64, 5000)
                except IOError as my_error:
                    log.error("genLoopPackets::timeout on read as well: %s", my_error)

            if self.ws_status > 0:
                tcount = 0
                log.debug("genLoopPackets: yielding")
                yield packet
                self.ws_status = 0

            # set the time every 24 hours (and initially after 20 loops to get initialisation done)
            if count > 20 and not self.time_set:
                self.setTime()
                self.time_set = True
                self.last_time_set += 86400
            elif self.time_set:
                if time.time() > self.last_time_set:
                    self.time_set = False

        # end while forever loop

    # end def genLoopPackets

    #--------------------------------------------------------------------------
    # genStartupRecords
    #--------------------------------------------------------------------------
    # the weewx engine call this function at the start when there are missing
    # records in the database.  This function retrieves them, yielding the
    # values that are greater than the input time back to the engine
    #--------------------------------------------------------------------------
    # since_ts: epoch time in seconds
    #--------------------------------------------------------------------------
    def genStartupRecords(self, since_ts):
        """Main function that gets the historic data from the console and calls decode to
        decode it.  It then yields newer records to the weewx engine"""

        self.use_archive_time = True
        self.last_ts = since_ts
        tcount = 0
        self.ws_status = 0

        log.debug("genStartupRecords: starting archive loop ... %d", since_ts)

        if not self.initialised:
            self.find_my_device()
            self.initialise_my_device()

        # set parameters
        usb_request = 0x09
        wvalue = 0x0200
        timeout = 30000  # Milliseconds (30 seconds)

        # create function from crcmod to check CRCs
        crcfunc = crcmod.predefined.mkCrcFun('xmodem')

        # Construct known binary messages
        hist_buf = struct.pack('BBBBBBBB',
                               0xFC,
                               0x05,
                               0x00,
                               0x00,
                               0x00,
                               0x08,
                               0x38,
                               0xFD)

        ack2_buf = struct.pack('BBBBBBBB',
                               0xFC,
                               0xD5,
                               0x01,
                               0x00,
                               0x00,
                               0x97,
                               0x0B,
                               0xFD)

        nack_buf = struct.pack('BBBBBBBB',
                               0xFC,
                               0xD5,
                               0x02,
                               0x00,
                               0x00,
                               0xCE,
                               0x5B,
                               0xFD)
        # do some looping
        packet = {}
        packet['usUnits'] = weewx.METRIC

        count = 0
        more_history = True
        bad_crc = False
        level = 0

        while more_history:
            count += 1

            # buf is the command passed to the console
            # if sleep is being used the 'now_buf' gets the latest
            # if sleep is not being used the 'ack2_buf' works well
            buf = ack2_buf
            if count == 1:
                buf = hist_buf
            elif bad_crc:
                buf = nack_buf
                bad_crc = False

            try:
                #retval =
                self.dev.ctrl_transfer(
                    0x21,         # USB Request Type
                    usb_request,  # USB Request
                    wvalue,       # WValue
                    0,            # Index
                    buf,          # Message
                    timeout)

                out = self.dev.read(0x81, 64, timeout)

                # check to see if this is of interest
                loc_a = out[0]
                loc_c = out[5]
                loc_d = out[63]
                level = 0
                loc_b1 = out[1]
                loc_b2 = out[2]
                loc_b3 = out[3]
                loc_b4 = out[4]

                # check for the case where the console has no data
                if loc_b1 == 0xff and loc_b2 == 0xff and loc_b3 == 0xff and loc_b4 == 0xff:
                    more_history = False

                if more_history and loc_a == 0xfe and (loc_b1 > 0 or loc_b2 > 0):
                    crc_ok = True
                    crc_a = crcfunc(out[0:63])
                    if loc_d != 0xfd or crc_a != 0:
                        crc_ok = False
                        bad_crc = True
                        log.warning("genStartupRecords: bad CRC")

                    if (loc_c == 0x11 or loc_c == 0x21 or loc_c == 0x31 or
                            loc_c == 0x41) and crc_ok:
                        self.in1 = bytearray(out)

                        if loc_c == 0x11:
                            level = 1
                            packet = self.decode(level)

                    elif (loc_c == 0x22 or loc_c == 0x32 or loc_c == 0x42) and crc_ok:
                        self.in2 = bytearray(out)

                        if loc_c == 0x22:
                            level = 2
                            packet = self.decode(level)

                    elif (loc_c == 0x33 or loc_c == 0x43) and crc_ok:
                        self.in3 = bytearray(out)

                        if loc_c == 0x33:
                            level = 3
                            packet = self.decode(level)

                    elif loc_c == 0x44 and crc_ok:
                        self.in4 = bytearray(out)
                        level = 4
                        packet = self.decode(level)

            # the exits below are good for the beta, better as pass
            # for issued version (and most not needed)
            except IOError as my_error:
                log.error("genStartupRecords::IOError error: %s", my_error)
                # the most likely explanation is a timeout
                tcount = tcount + 1
                count = 0
                if tcount > 5:
                    log.critical("genStartupRecords::IOError critical (too many timeouts): %s",
                                 my_error)
                    exit()
                try:
                    out = self.dev.read(0x81, 64, 5000)
                except IOError as my_error:
                    log.error("genStartupRecords::timeout on read as well: %s", my_error)

                log.error("genStartupRecords::IOError error: %s", my_error)

            if self.ws_status > 0:
                # check that time is the wanted range (or not set)
                if since_ts == None:
                    log.debug("genStartupRecords: yielding (null ts)")
                    yield packet
                    
                elif packet['dateTime'] > since_ts:
                    log.debug("genStartupRecords: yielding")
                    yield packet

                tcount = 0
                self.ws_status = 0

            # need to check if this was the last history item
            if level > 0:
                if loc_b1 == loc_b3 and loc_b2 == loc_b4:
                    more_history = False

        # end while still getting history

    # end def genStartupRecords

    #--------------------------------------------------------------------------
    # setTime
    #--------------------------------------------------------------------------
    # Function to set the time in the console to the current local time
    # This is done with 2 usb calls, the first sets the day, the second set
    # the time.  Note time is only updated to nearest second
    #
    # Assumes local time with summertime correction is wanted.
    #
    #--------------------------------------------------------------------------
    def setTime(self):
        """uses local date and time to set the consoles date and time"""

        # create function from crcmod to check CRCs
        crcfunc = crcmod.predefined.mkCrcFun('xmodem')

        # First get the date and time
        my_now = datetime.now()
        my_year = my_now.year - 2000
        my_month = my_now.month
        my_day = my_now.day

        # create buffer for date
        date_buf = struct.pack('BBBBBBBB',
                               0xFC, 0x08, my_year, my_month, my_day, 0x00, 0x00, 0xFD)
        crc = crcfunc(date_buf[0:5])
        crc1 = crc>>8
        crc2 = crc - (crc1<<8)
        date_buf = struct.pack('BBBBBBBB',
                               0xFC, 0x08, my_year, my_month, my_day, crc1, crc2, 0xFD)

        # set parameters
        usb_request = 0x09
        wvalue = 0x0200
        timeout = 30000  # Milliseconds

        # tranfer date
        try:
            #retval =
            self.dev.ctrl_transfer(
                0x21,         # USB Request Type
                usb_request,  # USB Request
                wvalue,       # WValue
                0,            # Index
                date_buf,     # Message
                timeout)

            #out=
            self.dev.read(0x81, 64, timeout)

            # get the time again (could be 10 seconds later ...)
            my_now = datetime.now()
            my_hour = my_now.hour
            my_min = my_now.minute
            my_sec = my_now.second

            # create buffer for time
            time_buf = struct.pack('BBBBBBBB',
                                   0xFC, 0x09, my_hour, my_min, my_sec, 0x00, 0x00, 0xFD)
            crc = crcfunc(time_buf[0:5])
            crc1 = crc>>8
            crc2 = crc - (crc1<<8)
            time_buf = struct.pack('BBBBBBBB',
                                   0xFC, 0x09, my_hour, my_min, my_sec, crc1, crc2, 0xFD)
            # no checking, it worked or it didn't ....

            #retval =
            self.dev.ctrl_transfer(
                0x21,         # USB Request Type
                usb_request,  # USB Request
                wvalue,       # WValue
                0,            # Index
                time_buf,     # Message
                timeout)

            #out=
            self.dev.read(0x81, 64, timeout)
            # no checking, it worked or it didn't ....

        except IOError as my_error:
            log.error("setTime IOError error: %s", my_error)

        except ValueError as my_error:
            log.error("setTime ValueError error: %s", my_error)

    # end def setTime

    #--------------------------------------------------------------------------
    # getTime
    #--------------------------------------------------------------------------
    # Function to get the time in the console
    #
    # There is a fundamental problem with the protocol for getting the time
    # The time is only returned to the nearest minute.
    #
    # given this limitation I have decided not to implement it at the moment.
    #
    # It could be implemented in the future but without very clever programming
    # will be 0 to 59 seconds slow.
    #
    #--------------------------------------------------------------------------
    #def getTime(self):
    # end def getTime(self)


    #--------------------------------------------------------------------------
    # genArchiveRecords
    #--------------------------------------------------------------------------
    # Deliberately not implemented.
    # The problem is that the only way to access the required record is to read
    # the data buffer from the beginning right to the end - potentially 14400
    # sets of records - not good, and this will happen every 5 minutes.
    #--------------------------------------------------------------------------
    # def genStartupRecords(self, since_ts):
    # end def genStartupRecords

# end class ws6in1
