import usb.core
import usb.util
import sys
import struct
import crcmod
from datetime import datetime
import time
import weedb
import weewx.drivers
import weeutil.weeutil

"""
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

When the history data is downloaded this is done in an identical way
to Section 1 except it start 0xfe01 and the date/time is the historic
date time and section 1 sets of 64 bytes are repeated multiple times -
for each recorded entry

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
0xfc030000002fa1fd : second command - seen a few times (possibly due to console command to update now)
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
DRIVER_NAME = 'WS6in1'
DRIVER_VERSION = "0.2"

#------------------------------------------------------------------------------
# loader
#------------------------------------------------------------------------------
# Required weewx driver function to return the instance of the ws6in1 driver
#
# config_dict: the configuration dictionary
# engine:      a reference to the weewx engine
#------------------------------------------------------------------------------
def loader(config_dict, engine):
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
    
    #-------------------------------------------------------
    # Constructor
    #-------------------------------------------------------
    def __init__(self, **stn_dict):
        self.initialised = False
        self.vendor  = 0x1941
        self.product = 0x8021
        self.model   = "WS6in1"
        self.last_rain = None
        self.ws_status = 0
        self.timeSet = False
        self.lastTimeSet = time.time()

    # end __init__

    # Unfortunately there is no provision to obtain the model from the station
    # itself, so use what is specified from the configuration file.
    @property
    def hardware_name(self):
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

        myStr=""
        end = False

        while self.index + 1 < len(self.buff) and end == False:
            myChar=str(chr(self.buff[self.index]))
            myStr = myStr + str(myChar)
            self.index = self.index + 1
            if self.buff[self.index] == 0x20:
                self.index=self.index+1
                end = True
        if myStr == "--.-":
            return None

        retVal = float(myStr)
        return retVal

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

        myStr=""
        end = False

        while self.index + 1 < len(self.buff) and end == False:
            myChar=str(chr(self.buff[self.index]))
            myStr = myStr + str(myChar)
            self.index = self.index + 1
            if self.buff[self.index] == 0x20 or self.buff[self.index] == 0x00:
                self.index=self.index+1
                end = True
        if myStr == "--":
            return None

        retVal = int(myStr)
        return retVal

    # end def get_int

    #-------------------------------------------------------
    # get_string
    #-------------------------------------------------------
    # Part of the decode sequence this looks at the next part
    # of the buffer and interprets it as a string.
    #-------------------------------------------------------
    def get_string(self):

        myStr=""
        end = False

        while self.index + 1 < len(self.buff) and end == False:
            myChar=str(chr(self.buff[self.index]))
            myStr = myStr + str(myChar)
            self.index = self.index + 1
            if self.buff[self.index] == 0x20:
                self.index=self.index+1
                end = True

        return myStr

    # end def get_string

    
    #-------------------------------------------------------
    # rain_delta
    #-------------------------------------------------------
    # works out the rain delta from the previous reading
    #
    # rain_in is the current rain reading (from midnight)
    #-------------------------------------------------------
    def rain_delta(self, rain_in):

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

        # weewx packet to be returned
        packet = {}
        

        # step 1 join the parts together
        j=0
        i = 0
        self.buff= bytearray()
        tmp = bytearray()
    
        #lots can go wrong in the decode .. if it does lets skip
        try:
            
            # loop for j = 1 to level
            j=1
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
                    print ("decode: unexpected level="+str(j))

                # construct the buffer
                j = j+1        
                k=7
                while k < 61:
                    self.buff.append(tmp[k])
                    buffSize = i+1;
                    i = i+1
                    k=k+1
                    if j > level and tmp[k] == 0x00:
                        self.buff.append(0x20) # end with a space
                        k=64

            # buff should contain the ascii values that are needed
            self.index = 0

            # get an integer - we throw this away
            rubbish = self.get_int()

            ws_date = self.get_string()

            ws_time = self.get_string()

            in_temp = self.get_float()

            in_humid = self.get_int()

            out_temp = self.get_float()

            out_humid = self.get_int()

            rain1 = self.get_float()

            rain2 = self.get_float()

            wind_speed = self.get_float()

            wind_gust = self.get_float()

            wind_dir_deg = self.get_int()

            wind_dir_str = self.get_string()

            barom_rel = self.get_int()

            barom_abs = self.get_int()

            uv_index = self.get_int()

            dewpoint = self.get_float()

            # not sure what this float is but discard
            rubbish2 = self.get_float()

            ## get the 7 temp/humidity sensor data
            ## I don't have one so cannot test except negatively
            extraTemp1  = self.get_float()
            extraHumid1 = self.get_int()
            extraTemp2  = self.get_float()
            extraHumid2 = self.get_int()
            extraTemp3  = self.get_float()
            extraHumid3 = self.get_int()
            extraTemp4  = self.get_float()
            extraHumid4 = self.get_int()
            extraTemp5  = self.get_float()
            extraHumid5 = self.get_int()
            extraTemp6  = self.get_float()
            extraHumid6 = self.get_int()
            extraTemp7  = self.get_float()
            extraHumid7 = self.get_int()

            # weewx time - use local time as its accurate (ntp, utc)
            my_time = int(time.time() + 0.5)

            # weewx uses packet ...
            packet['usUnits'] = weewx.METRIC
            packet['dateTime'] = my_time
            packet['inTemp'] = in_temp
            packet['inHumidity'] = in_humid
            packet['outTemp'] = out_temp
            packet['outHumidity'] = out_humid
            packet['dayRain']  = rain1 * 0.1 # convert to cm
            packet['hourRain'] = rain2 * 0.1 # convert to cm
            packet['rain'] = self.rain_delta(rain1) * 0.1 # convert to cm
            packet['windSpeed'] = wind_speed
            packet['windGust'] = wind_gust
            packet['windDir'] = wind_dir_deg
            packet['pressure'] = barom_abs
            packet['barometer'] = barom_rel
            packet['UV'] = uv_index
            packet['dewpoint'] = dewpoint
            packet['extraHumid1'] = extraHumid1
            packet['extraHumid2'] = extraHumid2
            packet['extraHumid3'] = extraHumid3
            packet['extraHumid4'] = extraHumid4
            packet['extraHumid5'] = extraHumid5
            packet['extraHumid6'] = extraHumid6
            packet['extraHumid7'] = extraHumid7
            packet['extraTemp1'] = extraTemp1
            packet['extraTemp2'] = extraTemp2
            packet['extraTemp3'] = extraTemp3
            packet['extraTemp4'] = extraTemp4
            packet['extraTemp5'] = extraTemp5
            packet['extraTemp6'] = extraTemp6
            packet['extraTemp7'] = extraTemp7
            self.ws_status = 1

        except:
            print ("unable to decode")
            pass

        return packet

    #end def decode

    #-------------------------------------------------------
    # find our device
    #-------------------------------------------------------
    # Expect to find the 6 in 1 (+7).  Not finding it is a
    # show stopper
    #-------------------------------------------------------
    def findMyDevice(self):

        self.dev = usb.core.find(idVendor=self.vendor, idProduct=self.product)

        if self.dev is None:
            print ("dev not found")
            raise ValueError('Device not found')

        # check if kernel driver
        print("success getting dev")

    # end findMyDevice

    #-------------------------------------------------------
    # initialiseMyDevice
    #-------------------------------------------------------
    # Various commands that initialise the weather station
    # before the main loop is initiated
    #-------------------------------------------------------
    def initialiseMyDevice(self):

        # check if the kernel has it ...
        if self.dev.is_kernel_driver_active(0):
            print("need to detach from the kernel")
            self.dev.detach_kernel_driver(0)
            print("detached")
            
        # reset the device
        self.dev.reset()

        # dev is known ... print some parameters
        print("dev.bLength            = "+str(self.dev.bLength))
        print("dev.bNumConfigurations = "+str(self.dev.bNumConfigurations))
        print("dev.bDeviceClass       = "+str(self.dev.bDeviceClass))

        # get the active configuration
        self.myCfg = self.dev.get_active_configuration()

        if self.myCfg is None:
            print ("cfg not found")
            raise ValueError('configuration not found')

        # cfg is known ... print some parameters
        print("success getting configuration")
        print("myCfg.bConfigurationValue = "+str(self.myCfg.bConfigurationValue))
        print("myCfg.bNumInterfaces      = "+str(self.myCfg.bNumInterfaces)+"\n")

        # set parameters
        usbRequestType = 0x0a
        wLength = 0

        # set to idle
        try:
            retval = dev.ctrl_transfer(
                0x21,            # USB Request Type
                usbRequestType,  # USB Request
                wLength)         # WValue

            print("Set idle done")

        except:
            print("Exception setting idle")
            pass

        # set parameters
        usbRequestType = 0x22
        WLength = 100

        # get HID Desriptor
        try:
            retval = dev.ctrl_transfer(
                0x81,            # USB Request Type
                usbRequestType,  # USB Request
                wLength)         # WValue

            print("Sent HID descriptor length")

        except:
            print("HID Descriptor got")
            pass

        self.initialised = True

        # set parameters
        usb_request = 0x09
        wvalue=0x0200
        timeout = 1300000  # Milliseconds
        decode_ok = False
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
            retval = self.dev.ctrl_transfer(
                0x21,         # USB Request Type
                usb_request,  # USB Request
                wvalue,       # WValue
                0,            # Index
                start_buf,    # Message
                timeout)

            out=self.dev.read(0x81,64,timeout)
            # not processing the initiatisation read ...
        except:
            print ("initialisation start failed")
            pass

    # end dev initialiseMyDevice


    #---------------------------------------------------------------
    # genLoopPackets
    #---------------------------------------------------------------
    # this is the main loop that sends commands and reads responses
    # it calls decode to write the output
    #---------------------------------------------------------------
    def genLoopPackets(self):

        print ("starting read loop ...")

        if not self.initialised:
            self.findMyDevice()
            self.initialiseMyDevice()

        # set parameters
        usb_request = 0x09
        wvalue=0x0200
        timeout = 1300000  # Milliseconds
        decode_ok = False

        # create function from crcmod to check CRCs
        crcfunc = crcmod.predefined.mkCrcFun('xmodem')

        # Construct known binary messages
        start_buf = struct.pack('BBBBBBBB',
                                0xFC,
                                0x07,
                                0x00,
                                0x00,
                                0x00,
                                0xE5,
                                0x50,
                                0xFD)

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
    
        ack1_buf = struct.pack('BBBBBBBB',
                               0xFC,
                               0xD4,
                               0x01,
                               0x00,
                               0x00,
                               0xE1,
                               0xBF,
                               0xFD)

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

        count  = 0
        while True:
            count += 1

            # buf is the command passed to the console
            # if sleep is being used the 'now_buf' gets the latest
            # if sleep is not being used the 'ack2_buf' works well
            buf = now_buf
            if count == 1:
                buf = now_buf
            elif count == 2:
                buf = ack1_buf

            #    uncomment this to get a history dump (at count  40 change ...)
            #elif count == 40:
            #    a_buf = hist_buf
            #    print("history")

            try:
                retval = self.dev.ctrl_transfer(
                    0x21,         # USB Request Type
                    usb_request,  # USB Request
                    wvalue,       # WValue
                    0,            # Index
                    buf,          # Message
                    timeout)

                out=self.dev.read(0x81,64,timeout)

                # check to see if this is of interest
                a = out[0]
                b = out[1]
                c = out[5]
                d = out[63]

                if a == 0xfe:
                    crc_ok = True
                    crc_a = crcfunc(out[0:63])
                    if d != 0xfd or crc_a != 0:
                        crc_ok = False
                        decode_ok = False
                        print ("bad CRC")

                    if (c == 0x11 or c == 0x21 or c == 0x31 or c == 0x41) and crc_ok:
                        self.in1 = bytearray(out)
                        decode_ok = True

                        if c == 0x11:
                            level = 1
                            packet = self.decode(level)

                    elif (c == 0x22 or c == 0x32 or c == 0x42) and decode_ok:
                        self.in2 = bytearray(out)

                        if c == 0x22:
                            level = 2
                            packet = self.decode(level)

                    elif (c == 0x33 or c == 0x43) and decode_ok:
                        self.in3 = bytearray(out)

                        if c == 0x33:
                            level = 3
                            packet = self.decode(level)

                    elif c == 0x44 and decode_ok:
                        self.in4 = bytearray(out)
                        level = 4
                        packet = self.decode(level)

                    elif not decode_ok:
                        pass
                    else:
                        print("unexpected value of c=" + str(c))

            # the exits below are good for the beta, better as pass
            # for issued version (and most not needed)
            except KeyboardInterrupt as e:
                exit()
            except IOError as e:
                print ("IOError error:", e)
                exit()
            except TypeError as e:
                print ("TypeError error:", e)
                exit()
            except NameError as e:
                print ("NameError error:", e)
                exit()
            except UnboundLocalError as e:
                print ("UnboundLocalError error:", e)
                exit()
            except ReferenceError as e:
                print ("ReferenceError error:", e)
                exit()
            except ValueError as e:
                print ("ValueError error:", e)
                exit()
            except RuntimeError as e:
                print ("RuntimeError error:", e)
                exit()
            except ArithmeticError as e:
                print ("ArithmeticError error:", e)
                exit()
            except AssertionError as e:
                print ("AssertionError error:", e)
                exit()
            except AttributeError as e:
                print ("AttributeError error:", e)
                exit()
            except LookupError as e:
                print ("LookupError error:", e)
                exit()
            except:
                print ("other unknown error")
                exit()

            if self.ws_status > 0:
                print("yielding")
                self.ws_status = 0
                yield packet

            # set the time every 24 hours (and initially after 20 loops to get initialisation done)
            if count > 20 and self.timeSet == False:
                self.setTime()
                self.timeSet = True
                self.lastTimeSet += 86400
            elif self.timeSet == True:
                if time.time() > self.lastTimeSet:
                    self.timeSet = False

        # end while forever loop

    # end def genLoopPackets

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

        # create function from crcmod to check CRCs
        crcfunc = crcmod.predefined.mkCrcFun('xmodem')

        # First get the date and time
        my_now = datetime.now()
        my_year  = my_now.year - 2000
        my_month = my_now.month
        my_day   = my_now.day

        # create buffer for date
        date_buf = struct.pack('BBBBBBBB',
                               0xFC, 0x08, my_year, my_month, my_day, 0x00, 0x00, 0xFD);
        crc=crcfunc(date_buf[0:5])
        crc1 = crc>>8
        crc2 = crc - (crc1<<8)
        date_buf = struct.pack('BBBBBBBB',
                               0xFC, 0x08, my_year, my_month, my_day, crc1, crc2, 0xFD);

        # set parameters
        usb_request = 0x09
        wvalue      = 0x0200
        timeout     = 10000  # Milliseconds

        # tranfer date
        try:
            retval = self.dev.ctrl_transfer(
                0x21,         # USB Request Type
                usb_request,  # USB Request
                wvalue,       # WValue
                0,            # Index
                date_buf,     # Message
                timeout)

            out=self.dev.read(0x81,64,timeout)

            # get the time again (could be 10 seconds later ...)
            my_now = datetime.now()
            my_hour  = my_now.hour
            my_min   = my_now.minute
            my_sec   = my_now.second

            # create buffer for time
            time_buf = struct.pack('BBBBBBBB',
                                   0xFC, 0x09, my_hour, my_min, my_sec, 0x00, 0x00, 0xFD);
            crc=crcfunc(time_buf[0:5])
            crc1 = crc>>8
            crc2 = crc - (crc1<<8)
            time_buf = struct.pack('BBBBBBBB',
                                   0xFC, 0x09, my_hour, my_min, my_sec, crc1, crc2, 0xFD);
            # no checking, it worked or it didn't ....
            
            retval = self.dev.ctrl_transfer(
                0x21,         # USB Request Type
                usb_request,  # USB Request
                wvalue,       # WValue
                0,            # Index
                time_buf,     # Message
                timeout)

            out=self.dev.read(0x81,64,timeout)
            # no checking, it worked or it didn't ....

        except IOError as e:
            print ("setTime IOError error:", e)
            pass
        except ReferenceError as e:
            print ("setTime ReferenceError error:", e)
            pass
        except ValueError as e:
            print ("setTime ValueError error:", e)
            pass
        except RuntimeError as e:
            print ("setTime RuntimeError error:", e)
            pass
        except ArithmeticError as e:
            print ("setTime ArithmeticError error:", e)
            pass
        except AttributeError as e:
            print ("setTime AttributeError error:", e)
            pass
        except:
            print ("setTime other unknown error")
            pass

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

# end class ws6in1
