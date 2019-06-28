import json
from collections import namedtuple
from pathlib import Path
from app.simulator.starship import Starship
from app.simulator.scene import Scene
from app.simulator.only_war import Report

SWORD = Path(__file__).resolve().parent / 'ship_types' / "sword.json"
TEMPEST = Path(__file__).resolve().parent / 'ship_types' / "tempest.json"


class Runner:
    def __init__(self):
        self.sheets = []
        self.report = Report()

    def add_sheet(self, ship_type, name, gunner, helmsman):
        if ship_type == 1:
            type_file = SWORD
        elif ship_type == 2:
            type_file = TEMPEST
        else:
            return
        with open(type_file) as jr:
            ship_repr = json.load(jr)
        ship_repr['ship'][0]["name"] = name
        ship_repr['ship'][0]["crew"]["helmsman_agility"] = helmsman
        ship_repr['ship'][0]["crew"]["gunner_agility"] = gunner
        self.sheets.append(ship_repr)

    def run(self):
        battle_scene = Scene(self.report)
        for sheet in self.sheets:
            ships = Starship.init_from_dict(sheet, self.report)
            battle_scene.create_new_team(ships)
        battle_scene.combat_loop()
        return battle_scene.looser