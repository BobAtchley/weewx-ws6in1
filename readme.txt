weewx-ws6in1
------------

weewx driver for the 6 in 1 PC weather station clones:
Youshiko YC9388
Bresser PC 6 in 1
Garni 935PC
Ventus W835

Installation
------------

0) install weewx (see the weewx user guide)

1) install required usb libraries pyusb and crcmod

pip install pyusb
pip install crcmod
pip install datetime

Note 1: if running weewx with python3 but python2 is the default python, use pip3
Note 2: if pip is not installed then install it first (e.g. sudo apt install
python-pip on a debian based linux distribution) replace with python3-pip for a
python3 install.

2) download the driver

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

Additional Notes
----------------

If weewx stops working (due to server problems etc) and there are missing
records, on startup weewx will attempt to restore these from the your weather
station console.  To be successful in the weewx.conf section "[StdArchive]" set
record_generation = hardware (the default is software).

The Archive_Interval in the weewx.conf section "[StdArchive]" controls how often
data is written to the database.  Default is 300 seconds.  If the console data
logger is not set to 5 minutes you may want to consider changing this to the
logger setting (but in seconds).

It is recommended you change your weather station console Data Log interval to
'5' minutes.  Please note this means after 50 days the weather station data log
will be full and it will no longer record data, so it is essential you
regularly clear the console data log (best practice would be after a successful
weewx database backup).  This can only be done at the weather station console.

Known Issues
------------

If weewx is started after clearing the data log on the console then timeout
errors might occur when there are no entries in the log.  The only cure found
so far is to wait for the console to have one item in its data log and then
re-start weewx.  Note if weewx is already running it does not appear to cause
any problems to clear the data log buffer.
