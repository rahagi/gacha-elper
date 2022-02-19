import os
import sys
import time
from typing import List, Literal, Optional, Callable, Union
import cv2
import numpy as np
from scipy import spatial
from .coordinate import Coordinate
from ..adb import Adb
from ..error import (
    ElperInvalidFindMode,
    ElperInvalidSimilarityRange,
    ElperInvalidCropBoundingBox,
)


class Elper:
    """
    Core of the elper utilities.

    `similarity_value` is the global similarity score limit whenever sim
    values aren't provided when using `find` methods.

    `find_path` defaults to current directory when isn't provided.
    """

    def __init__(self, similarity_value=0.8, find_path=""):
        self.similarity_value = similarity_value
        self.find_path = find_path or (os.path.split(sys.argv[0])[0] or ".")
        self.current_screen = np.array([[]])

    @staticmethod
    def __get_current_screen(bgr=0):
        img = None
        while img is None:
            img = cv2.imdecode(
                np.frombuffer(Adb.exec_out("screencap -p"), dtype=np.uint8), bgr
            )
        return img

    @staticmethod
    def __fix_coords(coords):
        try:
            fixed_coords = [coords[0]]
            for coord in coords:
                if coord not in fixed_coords:
                    fixed_coords.append(coord)
            return fixed_coords
        except IndexError:
            return []

    @staticmethod
    def __validate_crop(crop_from: Coordinate, crop_to: Coordinate):
        if (crop_from.x > crop_to.x) or (crop_from.y > crop_to.y):
            raise ElperInvalidCropBoundingBox()

    def __validate_sim(self, sim_from, sim_to):
        if not sim_from:
            sim_from = self.similarity_value
        if not sim_to:
            sim_to = self.similarity_value
        if sim_to > sim_from:
            raise ElperInvalidSimilarityRange()
        return (sim_from, sim_to)

    def __update_screen(self, bgr=0, crop_from=None, crop_to=None):
        self.current_screen = self.__get_current_screen(bgr)
        if crop_from and crop_to:
            self.__validate_crop(crop_from, crop_to)
            self.current_screen = self.current_screen[
                crop_from.y : crop_to.y, crop_from.x : crop_to.x
            ]

    def __delete_screen(self):
        self.current_screen = np.array([[]])

    def __find(self, template, similarity=None):
        similarity = similarity if similarity else self.similarity_value
        img_template = cv2.imread(f"{self.find_path}/{template}", 0)
        match = cv2.matchTemplate(
            self.current_screen, img_template, cv2.TM_CCOEFF_NORMED
        )
        value, coord = cv2.minMaxLoc(match)[1], cv2.minMaxLoc(match)[3]
        if value >= similarity:
            return Coordinate(coord[0], coord[1])
        return None

    def __find_multi(self, template, similarity=None):
        img_template = cv2.imread(f"{self.find_path}/{template}", 0)
        match = cv2.matchTemplate(
            self.current_screen, img_template, cv2.TM_CCOEFF_NORMED
        )
        coords = np.where(match >= similarity)
        coords = list(zip(coords[1], coords[0]))
        fixed_coords = self.__fix_coords([Coordinate(x, y) for x, y in coords])
        if fixed_coords:
            return fixed_coords
        return []

    def __wait_until(
        self,
        what: Literal["find", "disappear"],
        template: str,
        sim_from: Optional[float] = None,
        sim_to: Optional[float] = None,
        crop_from: Optional[Coordinate] = None,
        crop_to: Optional[Coordinate] = None,
        interval: float = 0,
        timeout: float = -1,
        other_cond: Callable = lambda: None,
    ):
        sim_from, sim_to = self.__validate_sim(sim_from, sim_to)
        start_time = time.time()
        while (
            not self.find(
                template,
                sim_from=sim_from,
                sim_to=sim_to,
                crop_from=crop_from,
                crop_to=crop_to,
            )
        ) == (what == "find"):
            time_diff = time.time() - start_time
            if other_cond():
                return
            if time_diff > timeout > 0:
                return
            self.wait(interval)

    def find(
        self,
        template: str,
        mode: Literal["single", "multi"] = "single",
        sim_from: Optional[float] = None,
        sim_to: Optional[float] = None,
        crop_from: Optional[Coordinate] = None,
        crop_to: Optional[Coordinate] = None,
        update_screen: bool = True,
    ) -> Union[List[Optional[Coordinate]], Coordinate]:
        """
        Find sub-image `template` in current screen with template matching.
        This will capture any occurence with similarty score from
        `sim_from` to `sim_to` where `sim_to` <= `sim_from`.

        `single` mode only return the `Coordinate` from the first occurence of `template`.

        `multi` mode return a list of `Coordinate`s of all occurences of `template`.

        Return `[]` when nothing is found.
        """
        result = []
        sim_from, sim_to = self.__validate_sim(sim_from, sim_to)
        if update_screen or not self.current_screen.any():
            self.__update_screen(crop_from=crop_from, crop_to=crop_to)
        while sim_from >= sim_to:
            if mode == "single":
                result = self.__find(template, sim_from)
                if result:
                    if update_screen:
                        self.__delete_screen()
                    return result
            elif mode == "multi":
                result += self.__find_multi(template, sim_from)
                result = self.__fix_coords(result)
            else:
                raise ElperInvalidFindMode()
            sim_from -= 0.01
        if update_screen:
            self.__delete_screen()
        return result

    def tap(
        self,
        coord: Coordinate,
        delay: float = 1.5,
        randomize: bool = True,
        random_radius: int = 15,
    ):
        """
        Execute `input tap` command from `adb` and
        wait for the amount of seconds defined in `delay`.
        """
        if randomize:
            coord = coord.randomize(random_radius)
        Adb.exec_out(f"input tap {coord.x} {coord.y}")
        self.wait(delay)

    def swipe(
        self,
        coord1: Coordinate,
        coord2: Coordinate,
        duration: float = 250,
        delay: float = 1.5,
    ):
        """
        Execute `input swipe` command from `adb` and
        wait for the amount of seconds defined in `delay`.
        """
        Adb.exec_out(
            f"input swipe {coord1.x} {coord1.y} {coord2.x} {coord2.y} {duration}"
        )
        self.wait(delay)

    def wait_until_find(
        self,
        template: str,
        sim_from: Optional[float] = None,
        sim_to: Optional[float] = None,
        crop_from: Optional[Coordinate] = None,
        crop_to: Optional[Coordinate] = None,
        interval: float = 0,
        timeout: float = -1,
        other_cond: Callable = lambda: None,
    ):
        """
        Pause execution until `template` appears on screen.
        If `other_cond` is provided it will get called on
        every iteration and stops this method when it returns `True`.

        If `timeout` is < 0, it means there is no timeout.

        `other_cond` must return bool value.
        """
        return self.__wait_until(
            what="find",
            template=template,
            sim_from=sim_from,
            sim_to=sim_to,
            crop_from=crop_from,
            crop_to=crop_to,
            interval=interval,
            timeout=timeout,
            other_cond=other_cond,
        )

    def wait_until_disappear(
        self,
        template: str,
        sim_from: Optional[float] = None,
        sim_to: Optional[float] = None,
        crop_from: Optional[Coordinate] = None,
        crop_to: Optional[Coordinate] = None,
        interval: float = 0,
        timeout: float = -1,
        other_cond: Callable = lambda: None,
    ):
        """
        Pause execution until `template` disappears from screen.
        If `other_cond` is provided it will get called on
        every iteration and stops this method when it returns `True`.

        If `timeout` is < 0, it means there is no timeout.

        `other_cond` must return bool value.
        """
        return self.__wait_until(
            what="disappear",
            template=template,
            sim_from=sim_from,
            sim_to=sim_to,
            crop_from=crop_from,
            crop_to=crop_to,
            interval=interval,
            timeout=timeout,
            other_cond=other_cond,
        )

    @staticmethod
    def find_closest(coords: List[Coordinate], coord: Coordinate) -> Coordinate:
        """
        Find the closest coordinate for `coord` from list of coordinates in `coords`.
        """
        coords = [(c.x, c.y) for c in coords]
        coord = (coord.x, coord.y)
        x, y = coords[spatial.KDTree(coords).query(coord)[1]]
        return Coordinate(x, y)

    @staticmethod
    def wait(secs: float):
        """
        Call `time.sleep` with the amount of `secs`.
        """
        time.sleep(secs)
