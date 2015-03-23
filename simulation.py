from actor import *
from skill import *
from job import *
from rotation import *

# TODO: support multiple players and enemies
class Simulation:
    def __init__(self, player, enemy, duration, rotation):
        self.player = player
        self.enemy = enemy
        self.rotation = rotation
        self.duration = duration

        self.time = 0
        self.tick_timer = 0 # Time until next TP/MP/DoT tick

    # Gets the amount of time that needs to pass until something important happens.
    def get_time_of_interest(self):
        return min(self.tick_timer, self.player.get_time_of_interest(),
                                    self.enemy.get_time_of_interest(),
                                    self.rotation.get_time_of_interest(self, self.player))

    def advance_time(self, time):
        self.time += time
        self.tick_timer = max(self.tick_timer - time, 0)

    def tick(self):
        if self.tick_timer == 0:
            self.player.tick()
            self.enemy.tick()
            self.tick_timer = 3

    # How should I prevent double checking of time?
    def run(self):
        while self.time < self.duration:
            self.rotation.use_skill(self, self.player, self.enemy)
            self.tick()

            time_of_interest = self.get_time_of_interest()
            if time_of_interest == 0:
                time_of_interest = 0.05 # Advance 0.05 sec if things don't appear to be moving

            self.advance_time(time_of_interest)
            self.player.advance_time(time_of_interest)
            self.enemy.advance_time(time_of_interest)

total_damage = 0
trials = 100
for i in xrange(0, trials):
    player = Actor(Bard)
    enemy = Actor(None)
    simulation = Simulation(player, enemy, 240, BardRotation)
    simulation.run()
    total_damage += enemy.potency * player.damage_per_potency / 240

print total_damage / trials