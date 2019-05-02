import json
import logging
import random

logger = logging.getLogger('__starship__')
logging.basicConfig(level=logging.DEBUG)


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
        self.helmsman_ag = 0
        self.gunner_ag = 0

    @classmethod
    def init_from_json(cls, json_repr):
        with open(json_repr) as jr:
            ship_repr = json.load(jr)
        ships = []
        for ship_item in ship_repr['ship']:
            ship_attributes = ship_item['attributes']
            ship = cls(ship_item['name'])
            ship.speed = ship_attributes['speed']
            ship.detection_bonus = ship_attributes['detection_bonus']
            ship.manouverability = ship_attributes['manouverability']
            ship.void_shield = ship_attributes['void_shield']
            ship.hull_integrity = ship_attributes['hull_integrity']
            ship.armour = ship_attributes['armour']
            ship.weapons = ship_attributes['weapons']
            ship_crew = ship_item["crew"]
            ship.helmsman_ag = ship_crew["helmsman_agility"]
            ship.gunner_ag = ship_crew["gunner_agility"]
            ships.append(ship)
        return ships

    def roll_initiative(self):
        return self.detection_bonus + random.randint(1, 10)

    def _roll_ballastic(self):
        roll = random.randint(1, 100)
        if self.gunner_ag < roll:
            return
        else:
            return (((self.gunner_ag - roll) // 10) + 1)

    def _roll(self, roll_expr):
        dice, addition = roll_expr.split('+')
        if dice == '1d10':
            roll = random.randint(1, 10)
        return roll + int(addition)

    def attempt_shots(self):
        battery_shots = {}
        for weapon in self.weapons:
            orientation = self.weapons[weapon]
            # TODO: if weapon orientation is valid
            success_rating = self._roll_ballastic()
            logger.debug("{} rolled {} successes on ballastic on {}".format(self.name, success_rating, weapon))
            if not success_rating:
                continue
            for battery in orientation:
                battery_shots[battery] = []
                logger.debug("Firing {} batteries on {}".format(battery, weapon))
                battery_stats = self.weapons[weapon][battery]
                if success_rating > battery_stats['strength']:
                    success_rating = battery_stats['strength']
                logger.debug("{} hits!".format(success_rating))
                for success in range(success_rating):
                    dmg = self._roll(battery_stats['damage'])
                    logger.debug("No.{} shot damage: {}".format(success, dmg))
                    battery_shots[battery].append(dmg)
        return battery_shots

    def bear_shots(self, shots):
        pass