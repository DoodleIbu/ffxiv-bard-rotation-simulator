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
    has_snapshot = False

    @staticmethod
    def tick(origin, target):
        pass

    @staticmethod
    def damage_modifier():
        return {}

class SilenceEffect(Effect):
    name = "Silence"
    duration = 1 # Some moves may give the same effect but have different durations

class InternalReleaseEffect(Effect):
    name = "Internal Release"
    duration = 15

    @staticmethod
    def damage_modifier():
        return {
            "critical_hit_rate_add": 0.10
        }

class BloodForBloodEffect(Effect):
    name = "Blood for Blood"
    duration = 15

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.10
        }

class RagingStrikesEffect(Effect):
    name = "Raging Strikes"
    duration = 20

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.20
        }

class HawksEyeEffect(Effect):
    name = "Hawk's Eye"
    duration = 20

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.13 # about
        }

class BarrageEffect(Effect):
    name = "Barrage"
    duration = 10

class StraightShotEffect(Effect):
    name = "Straight Shot"
    duration = 20

    @staticmethod
    def damage_modifier():
        return {
            "critical_hit_rate_add": 0.10
        }

class StraighterShotEffect(Effect):
    name = "Straighter Shot"
    duration = 10

class XPotionOfDexterityEffect(Effect):
    name = "Medicated"
    duration = 15

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.11 # about
        }

class FlamingArrowEffect(Effect):
    name = "Flaming Arrow"
    duration = 30

    @staticmethod
    def tick(origin, target):
        target.add_damage(30, snapshot)

class VenomousBiteEffect(Effect):
    name = "Venomous Bite"
    duration = 18

    @staticmethod
    def tick(origin, target):
        result = target.add_damage(35, snapshot)
        if result["critical_hit"] is True and random.random() < 0.5:
            origin.set_cooldown(Bloodletter, 0)

class WindbiteEffect(Effect):
    name = "Windbite"
    duration = 18

    @staticmethod
    def tick(origin, target, snapshot):
        result = target.add_damage(45, snapshot)
        if result["critical_hit"] is True and random.random() < 0.5:
            origin.set_cooldown(Bloodletter, 0)

# Data on skills
class Skill:
    name = ""
    animation_lock = 0
    cooldown = 0
    tp_cost = 0

    @staticmethod
    def use(origin, target):
        pass

class InternalRelease(Skill):
    name = "Internal Release"
    animation_lock = SHORT_DELAY
    cooldown = 60

    @staticmethod
    def use(origin, target):
        origin.add_effect(InternalReleaseEffect)

class BloodForBlood(Skill):
    name = "Blood for Blood"
    animation_lock = SHORT_DELAY
    cooldown = 80

    @staticmethod
    def use(origin, target):
        origin.add_effect(BloodForBloodEffect)

class RagingStrikes(Skill):
    name = "Raging Strikes"
    animation_lock = SHORT_DELAY
    cooldown = 120

    @staticmethod
    def use(origin, target):
        origin.add_effect(RagingStrikesEffect)

class HawksEye(Skill):
    name = "Hawk's Eye"
    animation_lock = SHORT_DELAY
    cooldown = 90

    @staticmethod
    def use(origin, target):
        origin.add_effect(HawksEyeEffect)

class Barrage(Skill):
    name = "Barrage"
    animation_lock = SHORT_DELAY
    cooldown = 90

    @staticmethod
    def use(origin, target):
        origin.add_effect(BarrageEffect)

class XPotionOfDexterity(Skill):
    name = "X-Potion of Dexterity"
    animation_lock = LONG_DELAY
    cooldown = 270

    @staticmethod
    def use(origin, target):
        origin.add_effect(XPotionOfDexterityEffect)

class HeavyShot(Skill):
    name = "Heavy Shot"
    animation_lock = GCD_DELAY
    tp_cost = 60

    @staticmethod
    def use(origin, target):
        if random.random() < 0.2:
            origin.add_effect(StraighterShotEffect)
        target.add_damage(origin.calculate_damage(150)["potency"])

class StraightShot(Skill):
    name = "Straight Shot"
    animation_lock = GCD_DELAY
    tp_cost = 70

    @staticmethod
    def use(origin, target):
        if origin.has_effect(StriaghterShotEffect):
            origin.remove_effect(StraighterShotEffect)
            target.add_damage(origin.calculate_damage(140, { "guaranteed_critical": True })["potency"])
        else:
            target.add_damage(origin.calculate_damage(140)["potency"])
        origin.add_effect(StraightShotEffect)

class VenomousBite(Skill):
    name = "Venomous Bite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @staticmethod
    def use(origin, target):
        target.add_damage(origin.calculate_damage(100)["potency"])
        target.add_effect(VenomousBiteEffect, origin)

class Windbite(Skill):
    name = "Windbite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @staticmethod
    def use(origin, target):
        target.add_damage(origin.calculate_damage(60)["potency"])
        target.add_effect(WindbiteEffect, origin)

class FlamingArrow(Skill): 
    name = "Flaming Arrow"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(origin, target):
        target.add_effect(FlamingArrowEffect, origin)

class BluntArrow(Skill):
    name = "Blunt Arrow"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(origin, target):
        target.add_damage(origin.calculate_damage(50)["potency"])
        target.add_effect(SilenceEffect, origin)

class RepellingShot(Skill):
    name = "Repelling Shot"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(origin, target):
        target.add_damage(origin.calculate_damage(80)["potency"])

class Bloodletter(Skill):
    name = "Bloodletter"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(origin, target):
        target.add_damage(origin.calculate_damage(150)["potency"])

class Invigorate(Skill):
    name = "Invigorate"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(origin, target):
        origin.add_tp(400)

class EffectTimer:
    def __init__(self, duration=0, snapshot=[]):
        self.duration = duration
        self.snapshot = snapshot

class Actor:
    def __init__(self):
        self.effects = {}

    def snapshot(self):
        return effects.keys()

    # Adds an effect to the actor.
    def add_effect(self, effect, origin):
        key = (effect, origin)
        effect_timer = None
        if effect.has_snapshot:
            effect_timer = EffectTimer(effect.duration, self.snapshot())
        else:
            effect_timer = EffectTimer(effect.duration)
        self.effects[key] = effect_timer

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

    # Does this belong here?
    def calculate_damage(self, potency, **kwargs):
        potency_modifier = 1.0
        critical_hit_rate = 0.2

        for effect_tuple in self.effects.keys():
            cls = effect_tuple[0]
            result = cls.damage_modifier()
            if "potency_multiply" in result:
                potency_modifier *= result["potency_multiply"]
            if "critical_hit_rate_add" in result:
                critical_hit_rate += result["critical_hit_rate_add"]

        critical_hit = False
        if random.random() < critical_hit_rate or kwargs.get("guaranteed_critical", False) is True:
            critical_hit = True

        return {
            "potency": potency * potency_modifier * (1 + critical_hit * 0.5)
            "critical_hit": critical_hit
        }

    def add_tp(value):
        if value >= 0:
            self.tp = min(self.tp + value, 1000)
        else:
            self.tp = max(self.tp - value, 0)

class Target(Actor):
    def __init__(self):
        self.damage = 0 # Damage in potency... for now.

    def calculate_dot_damage(self, potency, **kwargs):
        pass

    # TODO: should pass in origin since we need critical hit rates.
    #       probably better to calculate damage in target since target debuffs like vulnerability up
    #       may apply?
    #       or calculate personal potency first and then pass it in to add_damage
    #       for now let's do calcs elsewhere
    def add_damage(self, potency):
        self.damage += potency

class Simulation:
    def __init__(self):
        pass

print "Moo!"