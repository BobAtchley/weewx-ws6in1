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

Note 1: if running weewx with python3 but python2 is the default python, use pip3
Note 2: if pip is not installed then install it first (e.g. sudo apt install python-pip on a debian based linux distribution)
replace with python3-pip for a python3 install.

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

