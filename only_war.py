from starship import Starship
from scene import Scene
import argparse
import logging
from pathlib import Path

logger = logging.getLogger('__only_war__')
logging.basicConfig(level=logging.INFO)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ship-sheets', type=Path, nargs=2,
                        required=True,
                        help='Paths of the opponent json ship sheets')
    return parser.parse_args()


def main():
    args = parse_arguments()
    json_repr_files = args.ship_sheets
    battle_scene = Scene()
    for sheet in json_repr_files:
        ships = Starship.init_from_json(sheet)
        battle_scene.create_new_team(ships)
    battle_scene.combat_loop()


if __name__ == "__main__":
    main()