import subprocess
from typing import List, Optional
from ..error import AdbNotFound, AdbNoDevices


class AdbError(Exception):
    pass


class Adb:
    """
    Wrapper class for some of `adb`'s core functionalities.
    """

    @classmethod
    def __run_cmd(cls, cmd: str, check_devices: bool = True) -> str:
        if check_devices and not cls.list_devices():
            raise AdbNoDevices()
        try:
            with subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE) as pipe:
                return pipe.communicate()[0].decode("utf-8")
        except FileNotFoundError:
            raise AdbNotFound()

    @classmethod
    def list_devices(cls) -> List[Optional[str]]:
        """
        Run `adb devices`
        """
        cmd = "adb devices"
        devices = cls.__run_cmd(cmd, check_devices=False)

        return [d.replace("\t", " ") for d in devices.replace("\n\n", "").split("\n")][
            1:
        ]

    @classmethod
    def connect(cls, address: str, port: str):
        """
        Run `adb connect`
        """
        cmd = f"adb connect {address}:{port}"
        return cls.__run_cmd(cmd)

    @classmethod
    def exec_out(cls, cmd: str):
        """
        Run `adb exec-out`
        """
        cmd = f"adb exec-out {cmd}"
        return cls.__run_cmd(cmd)
