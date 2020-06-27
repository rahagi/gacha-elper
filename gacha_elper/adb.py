import subprocess
import sys

class Adb:
    @classmethod
    def connect(self, address, port):
        subprocess.call(f'adb connect {address}:{port}'.split(' '))

    @classmethod
    def exec_out(self, cmd):
        return subprocess.Popen(
            f'adb exec-out {cmd}'.split(' '), stdout=subprocess.PIPE
        ).communicate()[0]

    @classmethod
    def shell(self, cmd):
        subprocess.call(f'adb shell {cmd}'.split(' '))