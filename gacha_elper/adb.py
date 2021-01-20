import subprocess
import sys

class Adb:
    @classmethod
    def list_devices(self):
        devices = subprocess.Popen('adb devices'.split(' '), stdout=subprocess.PIPE).communicate()[0]
        return [x.replace('\t', ' ') for x in devices.decode('utf-8').replace('\n\n', '').split('\n')][1:]

    @classmethod
    def connect(self, address, port):
        return subprocess.Popen(f'adb connect {address}:{port}'.split(' '),
                stdout=subprocess.PIPE).communicate()[0]

    @classmethod
    def exec_out(self, cmd):
        return subprocess.Popen(
            f'adb exec-out {cmd}'.split(' '), stdout=subprocess.PIPE
        ).communicate()[0]

    @classmethod
    def shell(self, cmd):
        subprocess.call(f'adb shell {cmd}'.split(' '))
