import json
import random


class Starship:
    def __init__(self, name):
        self.name = name
        self.speed = 0
        self.detection_bonus = 0
        self.manouverability = 0
        self.void_shield = 0
        self.hull_integrity = 0
        self.armour = 0
        self.weapons = None

    @classmethod
    def init_from_json(cls, json_repr):
        with open(json_repr) as jr:
            ship_repr = json.load(jr)
        ships = []
        for ship in  ship_repr['ship']:
            ship_attributes = ship['attributes']
            ship = cls(ship['name'])
            ship.speed = ship_attributes['speed']
            ship.detection_bonus = ship_attributes['detection_bonus']
            ship.manouverability = ship_attributes['manouverability']
            ship.void_shield = ship_attributes['void_shield']
            ship.hull_integrity = ship_attributes['hull_integrity']
            ship.armour = ship_attributes['armour']
            ship.weapons = ship_attributes['weapons']
            ships.append(ship)
        return ships

    def roll_initiative(self):
        return self.detection_bonus + random.randint(1, 10)