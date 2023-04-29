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
    def __run_cmd(cls, cmd: str, check_devices: bool = True) -> bytes:
        if check_devices and not cls.list_devices():
            raise AdbNoDevices()
        try:
            with subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE) as pipe:
                return pipe.communicate()[0]
        except FileNotFoundError:
            raise AdbNotFound()

    @classmethod
    def list_devices(cls) -> List[Optional[str]]:
        """
        Run `adb devices`
        """
        cmd = "adb devices"
        devices = cls.__run_cmd(cmd, check_devices=False).decode("utf-8")

        return [d.replace("\t", " ") for d in devices.replace("\n\n", "").split("\n")][
            1:
        ]

    @classmethod
    def connect(cls, address: str, port: str):
        """
        Run `adb connect`
        """
        cmd = f"adb connect {address}:{port}"
        return cls.__run_cmd(cmd).decode("utf-8")

    @classmethod
    def exec_out(cls, cmd: str):
        """
        Run `adb exec-out`
        """
        cmd = f"adb exec-out {cmd}"
        print(f"entering {cmd}")
        res = cls.__run_cmd(cmd)
        print(f"exiting {cmd}")
        return res

    @classmethod
    def shell(cls, cmd: str):
        """
        Run `adb shell`
        """
        cmd = f"adb shell {cmd}"
        print(f"entering {cmd}")
        res = cls.__run_cmd(cmd)
        print(f"exiting {cmd}")
        return res
