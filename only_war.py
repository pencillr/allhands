from starship import Starship
from scene import Scene
import argparse
import logging
from pathlib import Path

logger = logging.getLogger('only_war')
logging.basicConfig(level=logging.DEBUG)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ship-sheets', type=Path, nargs=2,
                        help='Paths of the json ship sheets' )
    return parser.parse_args()


def main():
    args = parse_arguments()
    json_repr_files = args.ship_sheets
    battle_scene = Scene()
    for sheet in json_repr_files:
        ships = Starship.init_from_json(sheet)
        battle_scene.create_new_team(ships)
    for opponent in battle_scene.initiate_generator():
        target = battle_scene.choose_target(opponent)
        print("Attacking: ", target.name)

if __name__ == "__main__":
    main()