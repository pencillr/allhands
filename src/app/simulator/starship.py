import json
import logging
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
        self.helmsman_ag = 0
        self.gunner_ag = 0
        self.logger = self._get_logger(name)
        self.report = None

    @classmethod
    def init_from_json(cls, json_repr, report):
        with open(json_repr) as jr:
            ship_repr = json.load(jr)
        return cls.init_common(ship_repr, report)

    @classmethod
    def init_from_dict(cls, dict_repr, report):
        return cls.init_common(dict_repr, report)

    @classmethod
    def init_common(cls, ship_repr, report):
        ships = []
        for ship_item in ship_repr['ship']:
            ship_attributes = ship_item['attributes']
            ship = cls(ship_item['name'])
            ship.speed = ship_attributes['speed']
            ship.detection_bonus = ship_attributes['detection_bonus']
            ship.manouverability = ship_attributes['manouverability']
            ship.void_shield = ship_attributes['void_shield']
            ship.void_shield_actual = ship_attributes['void_shield']
            ship.hull_integrity = ship_attributes['hull_integrity']
            ship.armour = ship_attributes['armour']
            ship.weapons = ship_attributes['weapons']
            ship_crew = ship_item["crew"]
            ship.helmsman_ag = ship_crew["helmsman_agility"]
            ship.gunner_ag = ship_crew["gunner_agility"]
            ship.is_crippled = False
            ship.report = report
            ships.append(ship)
        return ships

    def _get_logger(self, name):
        logger = logging.getLogger('__{}__'.format(name))
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(name)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def roll_initiative(self):
        return self.detection_bonus + random.randint(1, 10)

    def _roll_ballastic(self):
        roll = random.randint(1, 100)
        self.logger.debug("Roll: {}".format(roll))
        if self.gunner_ag < roll:
            return 0
        else:
            return (((self.gunner_ag - roll) // 10) + 1)

    def _roll(self, roll_expr):
        dice, addition = roll_expr.split('+')
        if dice == '1d10':
            roll = random.randint(1, 10)
        return roll + int(addition)

    def reset_shields(self):
        self.void_shield_actual = self.void_shield

    def attempt_shots(self):
        if self.is_crippled:
            return
        battery_shots = {}
        for weapon in self.weapons:
            orientation = self.weapons[weapon]
            # TODO: if weapon orientation is valid
            self.logger.debug("Firing weapons on {}".format(weapon))
            self.report.write("Firing weapons on {}".format(weapon))
            for battery in orientation:
                success_rating = self._roll_ballastic()
                if success_rating:
                    success_message = "{} succeeded with rating {} on ballastic with {}".format(self.name, success_rating - 1, battery)
                    self.logger.debug(success_message)
                    self.report.write(success_message)
                else:
                    fail_message = "{} failed on ballastic roll with {}".format(self.name, battery)
                    self.logger.debug(fail_message)
                    self.report.write(fail_message)
                if not success_rating:
                    continue
                battery_shots[battery] = []
                battery_stats = self.weapons[weapon][battery]
                if success_rating - 1 == battery_stats['crit_rating']:
                    self.logger.debug("Critical hit! with battery {}".format(battery))
                    self.report.write("Critical hit! with battery {}".format(battery))
                if success_rating > battery_stats['strength']:
                    success_rating = battery_stats['strength']
                firing_message = "Firing {} batteries on {} {} times".format(battery, weapon, success_rating)
                self.logger.debug(firing_message)
                self.report.write(firing_message)
                self.logger.debug("{} hits!".format(success_rating))
                self.report.write("{} hits!".format(success_rating))
                for success in range(success_rating):
                    dmg = self._roll(battery_stats['damage'])
                    self.logger.debug("No.{} shot damage: {}".format(success, dmg))
                    self.report.write("No.{} shot damage: {}".format(success, dmg))
                    battery_shots[battery].append(dmg)
        return battery_shots

    def bear_shots(self, shots):
        full_dmg = 0
        for shot in shots:
            if self.void_shield_actual <= 0:
                full_dmg += int(shot)
            else:
                self.void_shield_actual -= 1
        full_dmg -= self.armour
        if full_dmg > 0:
            self.logger.info("Full damage taken: {}".format(full_dmg))
            self.report.write("Full damage taken: {}".format(full_dmg))
            self.hull_integrity -= full_dmg
            self.logger.info("Hull integrity: {}".format(self.hull_integrity))
            self.report.write("Hull integrity: {}".format(self.hull_integrity))
            if self.hull_integrity <= 0:
                self.logger.info("{} is crippled!".format(self.name))
                self.report.write("{} is crippled!".format(self.name))
                self.is_crippled = True
        else:
            self.logger.info("No significant damage on {}!".format(self.name))
            self.report.write("No significant damage on {}!".format(self.name))
