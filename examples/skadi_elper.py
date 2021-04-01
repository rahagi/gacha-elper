from gacha_elper.elper import Elper as Elp
from gacha_elper.elper import Coordinate as Coord

buttons = {
    "home1": Coord(215, 30),
    "home2": Coord(73, 230),
    "back": Coord(70, 35),
    "combat_skadi": Coord(927, 255),
    "operation_map": Coord(766, 385),
    "gt_5": Coord(682, 376),
    "gt_6": Coord(774, 282),
    "auto_deploy": Coord(919, 616),
    "start_battle1": Coord(913, 666),
    "start_battle2": Coord(888, 475),
}


def start():
    elp = Elp(find_path="./assets")
    if not elp.find("combat.png"):
        print("going home")
        elp.tap(buttons["home1"])
        elp.tap(buttons["home2"])
    elp.tap(buttons["combat_skadi"])
    elp.wait(1.5)
    elp.tap(buttons["operation_map"])
    gt_5 = True
    gt_5_count = 0
    try:
        while True:
            current_map = buttons["gt_5"] if gt_5 else buttons["gt_6"]
            elp.tap(current_map)
            if not elp.find("auto_enabled.png"):
                elp.tap(buttons["auto_deploy"])
            elp.tap(buttons["start_battle1"], 2.5)
            elp.tap(buttons["start_battle2"])
            elp.wait(35)
            elp.wait_until_find("trust.png")
            elp.tap(Coord(512, 512))
            elp.wait(7.5)
            elp.tap(buttons["back"])
            if gt_5:
                gt_5_count += 1
            if gt_5 and gt_5_count == 2:
                gt_5 = not gt_5
                gt_5_count = 0
            elif not gt_5:
                gt_5 = not gt_5
    except KeyboardInterrupt:
        print("done.")


if __name__ == "__main__":
    start()
