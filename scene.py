import logging
import random

logger = logging.getLogger('__scene__')
logging.basicConfig(level=logging.INFO)


class Scene:
    def __init__(self):
        self.teams = {}
        self.available_teams = {'gamma', 'delta'}

    def _add_team(self):
        name = self.available_teams.pop()
        if not name:
            raise ValueError("Cannot assign more teams!")
        self.teams[name] = []
        return name

    def add_ships_to_team(self, team, ship):
        self.teams[team].append(ship)

    def create_new_team(self, ships):
        team_name = self._add_team()
        for ship in ships:
            self.add_ships_to_team(team_name, ship)

    def initiate_generator(self):
        init_order = []
        for team, ships in self.teams.items():
            for ship in ships:
                init_order.append(
                    {
                        'initiative': ship.roll_initiative(),
                        'opponent': ship,
                        'team': team
                    })
        init_order.sort(key=lambda x: x['initiative'], reverse=True)
        for opponent in init_order:
            logger.debug("{} at team {} rolled initiative: {}".format(
                opponent['opponent'].name, opponent['team'], opponent['initiative']))
            yield opponent['opponent']

    def choose_target(self, attacker):
        for team, ships in self.teams.items():
            for ship in ships:
                if ship == attacker:
                    friendly_team = team
        target_team = friendly_team
        while target_team == friendly_team:
            target_team = random.choice(list(self.teams.keys()))
        return random.choice(self.teams[target_team])

    def combat_round(self, opponent, target):
        battery_shots = opponent.attempt_shots()
        if battery_shots:
            for battery in battery_shots:
                target.bear_shots(battery_shots[battery])
        else:
            logger.info("Miss!")

    def battle_keeps_going_check(self):
        for team in self.teams:
            d_count = 0
            ships = self.teams[team]
            for ship in ships:
                if ship.is_crippled:
                    d_count += 1
            if d_count >= len(ships):
                logger.info("{} team has no more ships.".format(team))
                return False
        return True

    def combat_loop(self):
        rounds = 1
        while self.battle_keeps_going_check():
            logger.info("Tactical round No.{}:".format(rounds))
            for opponent in self.initiate_generator():
                target = self.choose_target(opponent)
                if not opponent.is_crippled:
                    logger.info("The {} is attacking: {}".format(opponent.name, target.name))
                    self.combat_round(opponent, target)
            rounds += 1