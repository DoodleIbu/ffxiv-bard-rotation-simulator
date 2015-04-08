from actor import *
from server import *
from skill import *
from rotation import *

import multiprocessing

# TODO: support multiple players and enemies
class Simulation:
    def __init__(self, player, enemy, duration, rotation):
        self.server = Server([player, enemy])
        self.player = player
        self.enemy = enemy
        self.rotation = rotation
        self.duration = duration
        self.time = 0

    # Gets the amount of time that needs to pass until something important happens.
    def get_time_of_interest(self):
        return min(self.server.get_time_of_interest(),
                   self.player.get_time_of_interest(),
                   self.enemy.get_time_of_interest(),
                   self.rotation.get_time_of_interest(self.server, self.player))

    def advance_time(self, time):
        self.time += time
        self.player.advance_time(time)
        self.enemy.advance_time(time)
        self.server.advance_time(time)

    def run(self):
        while self.time < self.duration:
            self.rotation.use_skill(self.server, self.player, self.enemy)
            self.advance_time(self.get_time_of_interest())

def worker(args):
    total_damage = 0

    for i in xrange(0, args["trials"]):
        player = Actor("Bard")
        enemy = Actor("Enemy")
        simulation = Simulation(player, enemy, args["duration"], BardRotation())
        simulation.run()
        total_damage += enemy.potency_received[player]["potency"] * player.damage_per_potency / args["duration"]

    return total_damage

if __name__ == "__main__":
    multiprocessing.freeze_support()
    count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=count)
    trials = 1000
    print sum(pool.map(worker, [{ "duration": 240, "trials": trials / count }] * count)) / trials
