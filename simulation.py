from actor import *
from skill import *
from job import *

# TODO: support multiple players and enemies
class Simulation:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.tick_timer = 0 # Time until next TP/MP/DoT tick

    # Gets the amount of time that needs to pass until something important happens.
    def get_time_of_interest(self):
        return min(self.tick_timer, self.player.get_time_of_interest(),
                                    self.enemy.get_time_of_interest())

    def run(self):
        RagingStrikes.use(self.player, self.enemy)
        BloodForBlood.use(self.player, self.enemy)
        StraightShot.use(self.player, self.enemy)
        HeavyShot.use(self.player, self.enemy)
        Windbite.use(self.player, self.enemy)
        WindbiteAura.tick(self.player, self.enemy)
        print self.enemy.potency

player = Actor(Bard)
enemy = Actor(None)
simulation = Simulation(player, enemy)
simulation.run()
