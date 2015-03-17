import random
import sys

# Bard rotation potency calculator.
GCD = 2.45
AUTO_ATTACK_DELAY = 3.04
CRITICAL_HIT_RATE = 0.197586
DAMAGE_PER_POTENCY = 2.4888
SHORT_DELAY = 0.7
LONG_DELAY = 1.1
GCD_DELAY = 1.0

# Data on status effects
# TODO: Consider stacking and overwritable effects
class Effect:
    name = ""
    duration = 0

class SilenceEffect(Effect):
    name = "Silence"
    duration = 1 # Some moves may give the same effect but have different durations

class InternalReleaseEffect(Effect):
    name = "Internal Release"
    duration = 15

class BloodForBloodEffect(Effect):
    name = "Blood for Blood"
    duration = 15

class RagingStrikesEffect(Effect):
    name = "Raging Strikes"
    duration = 20

class HawksEyeEffect(Effect):
    name = "Hawk's Eye"
    duration = 20

class BarrageEffect(Effect):
    name = "Barrage"
    duration = 10

class StraightShotEffect(Effect):
    name = "Straight Shot"
    duration = 20

class StraighterShotEffect(Effect):
    name = "Straighter Shot"
    duration = 10

class XPotionOfDexterityEffect(Effect):
    name = "Medicated"
    duration = 15

class FlamingArrowEffect(Effect):
    name = "Flaming Arrow"
    duration = 30

class VenomousBiteEffect(Effect):
    name = "Venomous Bite"
    duration = 18

class WindbiteEffect(Effect):
    name = "Windbite"
    duration = 18

# Data on skills
class Skill:
    name = ""
    animation_lock = 0
    cooldown = 0
    tp_cost = 0

    def use(self, player, target):
        pass

class InternalRelease(Skill):
    name = "Internal Release"
    animation_lock = SHORT_DELAY
    cooldown = 60

    def use(self, player, target):
        player.add_effect(InternalReleaseEffect)

class BloodForBlood(Skill):
    name = "Blood for Blood"
    animation_lock = SHORT_DELAY
    cooldown = 80

    def use(self, player, target):
        player.add_effect(BloodForBloodEffect)

class RagingStrikes(Skill):
    name = "Raging Strikes"
    animation_lock = SHORT_DELAY
    cooldown = 120

    def use(self, player, target):
        player.add_effect(RagingStrikesEffect)

class HawksEye(Skill):
    name = "Hawk's Eye"
    animation_lock = SHORT_DELAY
    cooldown = 90

    def use(self, player, target):
        player.add_effect(HawksEyeEffect)

class Barrage(Skill):
    name = "Barrage"
    animation_lock = SHORT_DELAY
    cooldown = 90

    def use(self, player, target):
        player.add_effect(BarrageEffect)

class XPotionOfDexterity(Skill):
    name = "X-Potion of Dexterity"
    animation_lock = LONG_DELAY
    cooldown = 270

    def use(self, player, target):
        player.add_effect(XPotionOfDexterityEffect)

class HeavyShot(Skill):
    name = "Heavy Shot"
    animation_lock = GCD_DELAY
    tp_cost = 60

    def use(self, player, target):
        if random.random() < 0.2:
            player.add_effect(StraighterShotEffect)

class StraightShot(Skill):
    name = "Straight Shot"
    animation_lock = GCD_DELAY
    tp_cost = 70

    def use(self, player, target):
        if player.has_effect(StriaghterShotEffect):
            player.remove_effect(StraighterShotEffect)
        player.add_effect(StraightShotEffect)

class VenomousBite(Skill):
    name = "Venomous Bite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    def use(self, player, target):
        target.add_effect(VenomousBiteEffect, player)

class Windbite(Skill):
    name = "Windbite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    def use(self, player, target):
        target.add_effect(WindbiteEffect, player)

class FlamingArrow(Skill): 
    name = "Flaming Arrow"
    animation_lock = SHORT_DELAY

    def use(self, player, target):
        target.add_effect(FlamingArrowEffect, player)

class BluntArrow(Skill):
    name = "Blunt Arrow"
    animation_lock = SHORT_DELAY

    def use(self, player, target):
        target.add_effect(SilenceEffect, player)

class RepellingShot(Skill):
    name = "Repelling Shot"
    animation_lock = SHORT_DELAY

    def use(self, player, target):
        pass

class Bloodletter(Skill):
    name = "Bloodletter"
    animation_lock = SHORT_DELAY

    def use(self, player, target):
        pass

class Invigorate(Skill):
    name = "Invigorate"
    animation_lock = SHORT_DELAY

    def use(self, player, target):
        player.add_tp(400)

class EffectTimer:
    def __init__(self):
        self.duration = 0
        self.snapshot = []`

class Actor:
    def __init__(self):
        self.effects = {}

    # Adds an effect to the actor.
    def add_effect(self, effect, origin):
        key = (effect, origin)
        self.effects[key] = effect.duration

    def remove_effect(self, effect, origin):
        key = (effect, origin)
        self.effects.pop(key, None)

    def has_effect(self, effect):
        key = (effect, origin)
        if key in self.effects:
            return True
        else:
            return False

class Player(Actor):
    def __init__(self, job):
        self.job = job
        self.tp = 1000

    def add_tp(value):
        if value >= 0:
            self.tp = min(self.tp + value, 1000)
        else:
            self.tp = max(self.tp - value, 0)

class Target(Actor):
    def __init__(self):
        self.potency = 0

class Simulation:
    def __init__(self):
        pass
