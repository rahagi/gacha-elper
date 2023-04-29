from typing import Optional
import cv2
import numpy as np
import lz4.block
from gacha_elper.adb.adb import Adb


class Screencap:
    byte_pointer = 0

    @staticmethod
    def __reposition_byte_pointer(byte_array):
        while(byte_array[Screencap.byte_pointer:Screencap.byte_pointer + 4] != b'BMZ1'):
            Screencap.byte_pointer += 1
            if Screencap.byte_pointer >= len(byte_array):
                return None
        return byte_array[Screencap.byte_pointer:]

    @staticmethod
    def __ascreencap_capture() -> np.ndarray:
        raw_compressed_screencap = Screencap.__reposition_byte_pointer(Adb.exec_out('ascreencap --pack 2 --stdout'))
        if raw_compressed_screencap is None: return np.array([[]])

        compressed_screencap_header = np.frombuffer(raw_compressed_screencap[:20], dtype=np.uint32)
        if compressed_screencap_header[0] != 828001602:
            compressed_screencap_header = compressed_screencap_header.byteswap()
            if compressed_screencap_header[0] != 828001602: return np.array([[]])

        _, uncompressed_size, _, width, height = compressed_screencap_header
        channel = 3
        try:
            screencap = lz4.block.decompress(raw_compressed_screencap[20:], uncompressed_size=uncompressed_size)
        except:
            return np.array([[]])
        screencap = np.frombuffer(screencap, dtype=np.uint8)
        try:
            screencap = screencap[-int(width * height * channel):].reshape(height, width, channel)
        except:
            return np.array([[]])
        screencap = cv2.flip(cv2.cvtColor(screencap, cv2.COLOR_BGR2GRAY), 0)

        return cv2.rotate(screencap, cv2.ROTATE_90_COUNTERCLOCKWISE) if width < height else screencap


    @staticmethod
    def capture() -> np.ndarray:
        return Screencap.__ascreencap_capture()
