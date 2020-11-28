weewx-ws6in1
------------

The weewx-ws6in1 driver supports weather stations that are believed to be
manufactured by CCL Electronics - https://cclel.com
That use a particular console that connects to PCs

These are rebadged and sold as clones by multiple outlets.  The ones known
to work with this driver are listed below:

The weewx driver for the 6 in 1 PC weather station clones:
Youshiko YC9388
Bresser PC 6 in 1 - 7002570
Garni 935PC
Ventus W835

It also supports 5 in 1 PC weather stations:
Bresser PC 5 in 1 - 7002571
Logia 5-in-1 PC - LOWSB510PB

NB: This driver is not compatible with the WiFi versions of these 6 in
1 weatherstations.  It is still possible to use weewx using a Software
Defined Radio (SDR) - search for SDR in the weewx wiki or Interceptor.

Installation
------------

Installation assumes python3 will be used (strongly recommended
python2 is out of support).

The installation also assumes a debian compatible linux distribution.  Replace
any 'apt' commands with your distributions equivalent (e.g. yum for red hat etc)

0) install weewx (see the weewx user guide)

1) install required usb libraries pyusb and crcmod

pip3 install pyusb
pip3 install crcmod
pip3 install datetime

Note 1: if running weewx with python2 then use pip2 instead of pip3
Note 2: if pip3 is not installed then install it first (e.g. sudo apt install
python3-pip on a debian based linux distribution) replace with python-pip for a
python2 install.

Some users have found it necessary to additionally install the crcmod from the repository:

sudo apt install python3-crcmod

2) download the WS6in1 driver

wget -O weewx-ws6in1.zip https://github.com/bobatchley/weewx-ws6in1/archive/master.zip

3) install the driver

wee_extension --install weewx-ws6in1.zip

Note: use sudo if you get permission errors.

4) configure the driver

wee_config --reconfigure

Note: use sudo if you get permission errors


5) start weewx

sudo /etc/init.d/weewx start

[ or if using systemd:
sudo systemctl start weewx
sudo systemctl enable weewx ]


Driver options
--------------
[WS6in1]
    # mandatory location of the driver
    driver = user.ws6in1

    # optional parameters with default values if not set
    model = WS6in1
    wsType = WS6in1

Both model and wsType are optional.

'model' can be used to desribe the weatherstation model e.g. model = "Garni 935PC"
'wsType' is ignored unless it is set to "WS5in1" which will cause the UV packet to
be suppressed (the WS5in1 has no UV sensor, the console by default gives a
misleading value of 0)

===============================================================================

csv_ws6in1
----------
This is a standalone program written in python3 that also gets installed into
the weewx/bin/user area.  It has no arguments.  It needs to run with sudo
unless the local user has usb permissions:

$ sudo ./csv_ws6in1
or
$ sudo python3 ./csv_ws6in1

When run from the command line it downloads the data from the WS6in1 console
and creates 2 files:
ws6in1_<date and time>.csv
ws6in1_<date and time>.raw

These can be used for analysis, debugging, etc
weewx should be stopped before this is used and restarted afterwards.

===============================================================================

Additional Notes
----------------

The Archive_Interval in the weewx.conf section "[StdArchive]" controls how often
data is written to the database.  Default is 300 seconds.  If the console data
logger is not set to 5 minutes you may want to consider changing this to the
logger setting (but in seconds).

It is recommended you change your weather station console Data Log interval to
'5' minutes.  Please note this means after 50 days the weather station data log
will be full and it will no longer record data, so it is essential you
regularly clear the console data log (best practice would be after a successful
weewx database backup).  This can only be done at the weather station console.

HeatIndex provided by the console is calculated differently to the
HeatIndex calculated by weewx.  If the weewx calculation is preferred
then the weewx.conf file should be modified like this:

[StdWXCalculate]
[[Calculations]]
heatindex = software

Rainrate on the console uses a sliding window of an hour to perform the
calculation as opposed to WeeWX which uses a sliding window of 900
seconds (15 minutes). After WeeWX has performed its calculation, the
result is scaled to an hour.  This can make a big difference to the
calculated rainrate.  If the weewx calculation is prefered then the
weewx.conf file should be modified like this:

[StdWXCalculate]
[[Calculations]]
rainRate = software

I now set the heatindex, rainRate and windchill to 'software' so that
these are compatible with the majority of other weather stations, but
this is user choice.

Weewx is backfilling lost values even if record_generation is set to
'software' If you do not want the backfill update the weewx.conf file
with:

[StdArchive]
no_catchup = True

Known Issues
------------

If weewx is started after clearing the data log on the console then timeout
errors might occur when there are no entries in the log.  The only cure found
so far is to wait for the console to have one item in its data log and then
re-start weewx.  Note if weewx is already running it does not appear to cause
any problems to clear the data log buffer.

The console uses local time (passed to it from the WS6in1 driver).
This is good in that the console will display the correct time, but
bad because it uses this time to store its data in the console.  The
driver will correct for this local time difference when backfilling.
However if Summertime is being used on the device this will cause
problems when the clocks change.  There are currently 2 options
1) live with the issue - probability of the backlog being needed
(i.e. server failure) when the clocks change is very low
2) Disable summertime on the device weewx is running on

Roadmap
-------

If requested I may update time to the console to use UTC + fixed time
zone.  This would mean the local device could use Summertime
correction but the console would use a fixed time (so would display 1
hour out for half the year).  This would eliminate the clock change
problem.
