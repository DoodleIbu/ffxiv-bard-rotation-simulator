from actor import *
from skill import *
from job import *

class Simulation:
    def __init__(self):
        pass

source = Actor(Bard)
target = Actor(None)
RagingStrikes.use(source, target)
BloodForBlood.use(source, target)
StraightShot.use(source, target)
HeavyShot.use(source, target)
Windbite.use(source, target)
WindbiteAura.tick(source, target)
print target.potency
