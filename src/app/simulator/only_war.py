from app.simulator.starship import Starship
from app.simulator.scene import Scene
import argparse
import logging
from pathlib import Path


class Report:
    def __init__(self):
        self.report = []

    def write(self, entry):
        self.report.append(entry)

    def get_reports(self):
        return self.report


def get_logger():
    logger = logging.getLogger('__only_war__')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def _start_standalone_battle(args):
    json_repr_files = args.ship_sheets
    report = Report()
    battle_scene = Scene(report)
    for sheet in json_repr_files:
        ships = Starship.init_from_json(sheet, report)
        battle_scene.create_new_team(ships)
    battle_scene.combat_loop()


def _single_rolls(args):
    logger = get_logger()
    json_repr = args.ship_sheet
    ships = Starship.init_from_json(json_repr, report)
    for ship in ships:
        logger.info("Rolls for {}".format(ship.name))
        logger.info("Initiative: {}".format(ship.roll_initiative()))
        strike_map = ship.attempt_shots()
        if strike_map:
            logger.info("Summing up:")
            for weapon, hits in strike_map.items():
                logger.info("With battery {} dealt {}".format(weapon, "+".join(str(x) for x in hits)))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-commands')

    standalone = subparsers.add_parser('standalone', help='Start a battle between a team of ships.')
    standalone.add_argument('--ship-sheets', type=Path, nargs='+',
                            required=True,
                            help='Paths of the opponent json ship sheets')
    standalone.set_defaults(func=_start_standalone_battle)

    single = subparsers.add_parser('single-run', help='Report the battle rolls of a single group of ships.')
    single.add_argument('--ship-sheet', type=Path,
                        required=True,
                        help='Paths of the opponent json ship sheets')
    single.set_defaults(func=_single_rolls)

    options = parser.parse_args()
    options.func(options)


if __name__ == "__main__":
    main()
