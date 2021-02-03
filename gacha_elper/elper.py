import time
import subprocess
import os
import sys
import cv2
import numpy as np
from random import randint
from scipy import spatial
from .adb import Adb

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__ (self, other):
        coord1 = self.x, self.y
        coord2 = other.x, other.y
        return spatial.distance.euclidean(coord1, coord2) < 10

    def __hash__(self):
        return hash((self.x, self.y))

    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def scale(self, n):
        return Coordinate(self.x+n, self.y+n)

    def randomize(self, radius=3):
        self.x += randint(-radius, radius)
        self.y += randint(-radius, radius)

class Elper:
    CURRENT_DIR = os.path.split(sys.argv[0])[0] or '.'
    SIMILARITY_VALUE = 0.8
    CURRENT_SCREEN = np.array([[]])

    @classmethod
    def __update_screen(self, bgr=0, crop_from=None, crop_to=None):
        self.CURRENT_SCREEN = self.__get_current_screen()
        if crop_from and crop_to:
            self.CURRENT_SCREEN = self.CURRENT_SCREEN[crop_from.y:crop_to.y, crop_from.x:crop_to.x]

    @classmethod
    def __get_current_screen(self, bgr=0):
        img = None
        while img is None:
            img = cv2.imdecode(np.frombuffer(Adb.exec_out('screencap -p'), dtype=np.uint8), bgr)
        return img

    @classmethod
    def __delete_screen(self):
        self.CURRENT_SCREEN = np.array([[]])

    @classmethod
    def __find(self, template, similarity=SIMILARITY_VALUE):
        img_template = cv2.imread(f'{self.CURRENT_DIR}/assets/{template}.png', 0)
        match = cv2.matchTemplate(self.CURRENT_SCREEN, img_template, cv2.TM_CCOEFF_NORMED)
        value, coord = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            return Coordinate(coord[0], coord[1])
        return None

    @classmethod
    def __find_multi(self, template, similarity=SIMILARITY_VALUE):
        img_template = cv2.imread(f'{self.CURRENT_DIR}/assets/{template}.png', 0)
        match = cv2.matchTemplate(self.CURRENT_SCREEN, img_template, cv2.TM_CCOEFF_NORMED)
        coords = np.where(match >= similarity)
        coords = list(zip(coords[1], coords[0]))
        fixed_coords = self.__fix_coords([Coordinate(x, y) for x, y in coords])
        if fixed_coords:
            return fixed_coords
        return []

    @classmethod
    def __fix_coords(self, coords):
        try:
            fixed_coords = [coords[0]]
            for coord in coords:
                if coord not in fixed_coords:
                    fixed_coords.append(coord)
            return fixed_coords
        except IndexError:
            return []

    @classmethod
    def find(self, template, mode=0, sim_from=SIMILARITY_VALUE, sim_to=SIMILARITY_VALUE,
            crop_from=None, crop_to=None, update_screen=True):
        result = []
        if update_screen or not self.CURRENT_SCREEN.any():
            self.__update_screen(crop_from=crop_from, crop_to=crop_to)
        while sim_from >= sim_to:
            if mode == 0:
                result = self.__find(template, sim_from)
                if result:
                    if update_screen:
                        self.__delete_screen()
                    return result
            else:
                result += self.__find_multi(template, sim_from)
                result = self.__fix_coords(result)
            sim_from -= 0.01
        if update_screen:
            self.__delete_screen()
        return result

    @classmethod
    def tap(self, coord, delay=1.5, randomize=True, random_radius=15):
        old_x, old_y = coord.x, coord.y
        if randomize:
            coord.randomize(radius=random_radius)
        Adb.shell(f'input tap {coord.x} {coord.y}')
        coord.x, coord.y = old_x, old_y
        self.wait(delay)

    @classmethod
    def swipe(self, coord1, coord2, duration=250, delay=1.5):
        Adb.shell(f'input swipe {coord1.x} {coord1.y} {coord2.x} {coord2.y} {duration}')
        self.wait(delay)

    @classmethod
    def find_closest(self, coords, coord):
        coords = [(c.x, c.y) for c in coords]
        coord = (coord.x, coord.y)
        x, y = coords[spatial.KDTree(coords).query(coord)[1]]
        return Coordinate(x, y)
    
    @classmethod
    def wait_until_find(self, template, sim_from=SIMILARITY_VALUE, sim_to=SIMILARITY_VALUE,
            crop_from=None, crop_to=None, interval=0, handler=lambda *x: None):
        while not self.find(template, sim_from=sim_from, sim_to=sim_to, crop_from=crop_from, crop_to=crop_to):
            if handler():
                return
            self.wait(interval)
    
    @classmethod
    def wait_until_disappear(self, template, sim_from=SIMILARITY_VALUE, sim_to=SIMILARITY_VALUE,
            crop_from=None, crop_to=None, interval=0, handler=lambda *x: None):
        while self.find(template, sim_from=sim_from, sim_to=sim_to, crop_from=crop_from, crop_to=crop_to):
            if handler():
                return
            self.wait(interval)

    @classmethod
    def wait(self, duration):
        time.sleep(duration)
