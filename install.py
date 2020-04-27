# installer for WS6in1 driver
# Copyright 2020 Bob Atchley

from setup import ExtensionInstaller

def loader():
    return WS6in1Installer()

class WS6in1Installer(ExtensionInstaller):
    def __init__(self):
        super(WS6in1Installer, self).__init__(
            version="0.2",
            name='WS6in1',
            description='Collect data from WS6in1 PC connected console',
            author="Bob Atchley",
            author_email="bob.atchley@gmail.com",
            files=[('bin/user', ['bin/user/ws6in1.py'])]
        )
