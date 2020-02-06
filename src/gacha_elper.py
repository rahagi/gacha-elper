import time
import subprocess
import cv2
import numpy as np
from datetime import datetime
from scipy import spatial
from src.adb import Adb

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__ (self, other):
        coord1 = self.x, self.y
        coord2 = other.x, other.y
        return spatial.distance.euclidean(coord1, coord2) < 10

    def __hash__(self):
        return hash((self.x, self.y, self.mob, self.siren))

    def __repr__(self):
        return f'({self.x}, {self.y})'

class GachaElper:
    SIMILARITY_VALUE = 0.8
    CURRENT_SCREEN = np.array([[]])

    @classmethod
    def __update_screen(self, bgr=0):
        self.CURRENT_SCREEN = self.__get_current_screen()

    @classmethod
    def __get_current_screen(self, bgr=0):
        img = None
        while img is None:
            img = cv2.imdecode(np.fromstring(Adb.exec_out('screencap -p'), dtype=np.uint8), bgr)
        return img

    @classmethod
    def __delete_screen(self):
        self.CURRENT_SCREEN = np.array([[]])

    @classmethod
    def __find(self, template, similarity=SIMILARITY_VALUE):
        img_template = cv2.imread(f'assets/{template}.png', 0)
        match = cv2.matchTemplate(self.CURRENT_SCREEN, img_template, cv2.TM_CCOEFF_NORMED)
        value, location = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            return Point(location[0], location[1])
        return None

    @classmethod
    def __find_multi(self, template, similarity=SIMILARITY_VALUE):
        img_template = cv2.imread(f'assets/{template}.png', 0)
        match = cv2.matchTemplate(self.CURRENT_SCREEN, img_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(match >= similarity)
        locations = list(zip(locations[1], locations[0]))
        fixed_locs = self.fix_locs([Point(x, y) for x, y in locations])
        if fixed_locs:
            return fixed_locs
        return []

    @classmethod
    def find(self, template, mode=0, sim_from=SIMILARITY_VALUE, sim_to=SIMILARITY_VALUE, update_screen=True):
        result = []
        if update_screen or not self.CURRENT_SCREEN.any():
            self.__update_screen()
        while sim_from >= sim_to:
            if mode == 0:
                result = self.__find(template, sim_from)
                if result:
                    if update_screen:
                        self.__delete_screen()
                    return result
            else:
                result += self.__find_multi(template, sim_from)
            sim_from -= 0.01
        if update_screen:
            self.__delete_screen()
        return result

    @classmethod
    def tap(self, dimension, delay=1.5):
        Adb.shell(f'input tap {dimension.x} {dimension.y}')
        self.wait(delay)

    @classmethod
    def swipe(self, dimension1, dimension2, duration=250):
        Adb.shell(f'input swipe {dimension1.x} {dimension1.y} {dimension2.x} {dimension2.y} {duration}')

    @classmethod
    def fix_locs(self, locs):
        try:
            fixed_locs = [locs[0]]
            for loc in locs:
                if loc not in fixed_locs:
                    fixed_locs.append(loc)
            return fixed_locs
        except IndexError:
            return []

    @classmethod
    def find_closest(self, coords, coord):
        x, y = coords[spatial.KDTree(coords).query(coord)[1]]
        return Point(x, y)

    @classmethod
    def wait(self, duration):
        time.sleep(duration)
    
    @classmethod
    def time_now(self):
        return datetime.now()

    @classmethod
    def time_elapsed(self, end, start):
        hours, remainder = divmod((end-start).seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        }
