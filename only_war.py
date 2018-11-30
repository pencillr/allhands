from starship import Starship
import argparse
import logging
from pathlib import Path

logger = logging.getLogger('only_war')
logging.basicConfig(level=logging.DEBUG)

# def initiate(opponents):
#     winner = {
#         'initiative': 0,
#         'name': None
#     }
#     for opponent in opponents:
#         i = opponent.roll_initiative()
#         print("{} rolled {}".format(opponent.name, str(i)))
#         if i > winner['initiative']:
#             winner['initiative'] = i
#             winner['name'] = opponent.name
#     print("First is {}".format(winner['name']))


def initiate_generator(opponents):
    init_order = []
    for opponent in opponents:
        init_order.append(
            {
                'initiative': opponent.roll_initiative(),
                'opponent': opponent
            })
    init_order.sort(key=lambda x: x['initiative'], reverse=True)
    for opponent in init_order:
        logger.debug("{} initiative: {}".format(
            opponent['opponent'].name, opponent['initiative']))
        yield opponent['opponent']


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ship-sheets', type=Path, nargs=2,
                        help='Paths of the json ship sheets' )
    return parser.parse_args()


def main():
    args = parse_arguments()
    json_repr_files = args.ship_sheets
    opponents = []
    for sheet in json_repr_files:
        opponents.append(Starship.init_from_json(sheet))
    for opponent in initiate_generator(opponents):
        print(opponent)


if __name__ == "__main__":
    main()