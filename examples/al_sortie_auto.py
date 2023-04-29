#!/usr/bin/env python3
import sys

from gacha_elper.elper import Coordinate as Coord
from gacha_elper.elper import Elper as Elp


REUSE_DOUBLE_REWARDS = True


class Button:
    BACK = Coord(50, 45)
    GO_1 = Coord(759, 487)
    GO_2 = Coord(864, 554)
    DISASSEMBLE = Coord(640, 530)
    SORT = Coord(345, 500)
    QR = Coord(614, 689)
    AUTO_SEARCH = Coord(1000, 590)
    CONTINUE = Coord(740, 560)


elp = Elp(find_path='./assets')


def wait_until_main():
    elp.wait_until_find(
        'auto_search.png', crop_from=Coord(930, 530), crop_to=Coord(1024, 670)
    )


def is_dock_full():
    elp.wait(2)
    return elp.find(
        'sort.png', crop_from=Coord(273, 444), crop_to=Coord(430, 510)
    )


def retire_ship():
    print('Retiring ship...')
    elp.wait(0.75)
    elp.tap(Button.SORT, randomize=False)
    elp.wait(3)
    elp.tap(Button.QR, randomize=False)
    elp.tap(Coord(808, 598), randomize=False)   # confirm2
    elp.tap(Coord(630, 484), randomize=False)   # confirm >=elite
    elp.tap(Coord(785, 621), randomize=False)   # Tap to continue
    elp.tap(Coord(765, 511), randomize=False)   # confirm3
    elp.tap(Button.DISASSEMBLE, randomize=False)
    elp.tap(Coord(785, 621), randomize=False)  # Tap to continue
    elp.tap(Button.BACK, randomize=False)
    wait_until_main()
    elp.wait(4)


def battle():
    def handle_full_dock():
        if is_dock_full():
            retire_ship()
            elp.tap(Button.AUTO_SEARCH, randomize=False)

    elp.wait_until_find(
        'continue.png',
        crop_from=Coord(200, 0),
        crop_to=Coord(810, 720),
        other_cond=handle_full_dock,
    )
    return elp.find('continue.png')


if __name__ == '__main__':
    try:
        print('waiting for you to enter a map')
        wait_until_main()
        print('entered a map')
        while True:
            continue_button = battle()
            if REUSE_DOUBLE_REWARDS:
                elp.tap(continue_button.transform(-20, 15), randomize=False)
            elp.tap(continue_button, randomize=False)
            if is_dock_full():
                retire_ship()
                elp.tap(Button.GO_1, randomize=False)
                elp.tap(Button.GO_2, randomize=False)
    except KeyboardInterrupt:
        print('stopping...')
        sys.exit(0)
