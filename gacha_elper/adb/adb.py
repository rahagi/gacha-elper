import subprocess


class Adb:
    """
    Wrapper class for some of `adb`'s core functionalities.
    """

    @classmethod
    def __run_cmd(cls, cmd: str):
        if not cls.list_devices():
            raise Exception("No emulator/device")
        return subprocess.Popen(cmd.split(" "), stdout=subprocess.PIPE).communicate()[0]

    @classmethod
    def list_devices(cls):
        cmd = "adb devices"
        devices = cls.__run_cmd(cmd)
        return [
            x.replace("\t", " ")
            for x in devices.decode("utf-8").replace("\n\n", "").split("\n")
        ][1:]

    @classmethod
    def connect(cls, address: str, port: str):
        cmd = f"adb connect {address}:{port}"
        return cls.__run_cmd(cmd)

    @classmethod
    def exec_out(cls, cmd: str):
        cmd = f"adb exec-out {cmd}"
        return cls.__run_cmd(cmd)