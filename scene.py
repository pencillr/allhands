import logging
import random

logger = logging.getLogger('scene')
logging.basicConfig(level=logging.DEBUG)


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
        enemy_team = friendly_team
        while enemy_team == friendly_team:
            enemy_team = random.choice(list(self.teams.keys()))
        return random.choice(self.teams[enemy_team])