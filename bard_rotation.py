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

# Helper class to calculate damage.
class DamageHelper:

    @staticmethod
    def calculate_damage(potency, source, **kwargs):
        potency_modifier = 1.0
        critical_hit_rate = source.base_critical_hit_rate

        for aura_tuple in source.auras.keys():
            cls = aura_tuple[0]
            result = cls.damage_modifier()
            potency_modifier *= result.get("potency_multiply", 1.0)
            critical_hit_rate += result.get("critical_hit_rate_add", 0.0)

        critical_hit = False
        if random.random() < critical_hit_rate or kwargs.get("guaranteed_critical", False) is True:
            critical_hit = True

        return {
            "potency": potency * potency_modifier * (1 + critical_hit * 0.5),
            "critical_hit": critical_hit
        }

    @staticmethod
    def calculate_dot_damage(potency, source, target, aura, **kwargs):
        potency_modifier = 1.0
        critical_hit_rate = source.base_critical_hit_rate

        aura_timer = target.auras.get((aura, source), None)
        for aura_tuple in aura_timer.snapshot:
            cls = aura_tuple[0]
            result = cls.damage_modifier()
            potency_modifier *= result.get("potency_multiply", 1.0)
            critical_hit_rate += result.get("critical_hit_rate_add", 0.0)

        critical_hit = False
        if random.random() < critical_hit_rate:
            critical_hit = True

        return {
            "potency": potency * potency_modifier * (1 + critical_hit * 0.5),
            "critical_hit": critical_hit
        }

# Data on auras
# TODO: Consider stacking and overwritable auras
class Aura:
    name = ""
    duration = 0
    has_snapshot = False

    @staticmethod
    def tick(source, target):
        pass

    @staticmethod
    def damage_modifier():
        return {}

class SilenceAura(Aura):
    name = "Silence"
    duration = 1 # Some moves may give the same aura but have different durations

class InternalReleaseAura(Aura):
    name = "Internal Release"
    duration = 15

    @staticmethod
    def damage_modifier():
        return {
            "critical_hit_rate_add": 0.10
        }

class BloodForBloodAura(Aura):
    name = "Blood for Blood"
    duration = 15

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.10
        }

class RagingStrikesAura(Aura):
    name = "Raging Strikes"
    duration = 20

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.20
        }

class HawksEyeAura(Aura):
    name = "Hawk's Eye"
    duration = 20

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.13 # about
        }

class BarrageAura(Aura):
    name = "Barrage"
    duration = 10

class StraightShotAura(Aura):
    name = "Straight Shot"
    duration = 20

    @staticmethod
    def damage_modifier():
        return {
            "critical_hit_rate_add": 0.10
        }

class StraighterShotAura(Aura):
    name = "Straighter Shot"
    duration = 10

class XPotionOfDexterityAura(Aura):
    name = "Medicated"
    duration = 15

    @staticmethod
    def damage_modifier():
        return {
            "potency_multiply": 1.11 # about
        }

class FlamingArrowAura(Aura):
    name = "Flaming Arrow"
    duration = 30
    has_snapshot = True

    @staticmethod
    def tick(source, target):
        result = DamageHelper.calculate_dot_damage(30, source, target, FlamingArrowAura)
        target.add_damage(result["potency"])

class VenomousBiteAura(Aura):
    name = "Venomous Bite"
    duration = 18
    has_snapshot = True

    @staticmethod
    def tick(source, target):
        result = DamageHelper.calculate_dot_damage(35, source, target, VenomousBiteAura)
        target.add_damage(result["potency"])
        if result["critical_hit"] is True and random.random() < 0.5:
            source.set_cooldown(Bloodletter, 0)

class WindbiteAura(Aura):
    name = "Windbite"
    duration = 18
    has_snapshot = True

    @staticmethod
    def tick(source, target):
        result = DamageHelper.calculate_dot_damage(45, source, target, WindbiteAura)
        target.add_damage(result["potency"])
        if result["critical_hit"] is True and random.random() < 0.5:
            source.set_cooldown(Bloodletter, 0)

# Data on skills
class Skill:
    name = ""
    animation_lock = 0
    cooldown = 0
    tp_cost = 0

    @staticmethod
    def use(source, target):
        pass

class InternalRelease(Skill):
    name = "Internal Release"
    animation_lock = SHORT_DELAY
    cooldown = 60

    @staticmethod
    def use(source, target):
        source.add_aura(InternalReleaseAura)

class BloodForBlood(Skill):
    name = "Blood for Blood"
    animation_lock = SHORT_DELAY
    cooldown = 80

    @staticmethod
    def use(source, target):
        source.add_aura(BloodForBloodAura)

class RagingStrikes(Skill):
    name = "Raging Strikes"
    animation_lock = SHORT_DELAY
    cooldown = 120

    @staticmethod
    def use(source, target):
        source.add_aura(RagingStrikesAura)

class HawksEye(Skill):
    name = "Hawk's Eye"
    animation_lock = SHORT_DELAY
    cooldown = 90

    @staticmethod
    def use(source, target):
        source.add_aura(HawksEyeAura)

class Barrage(Skill):
    name = "Barrage"
    animation_lock = SHORT_DELAY
    cooldown = 90

    @staticmethod
    def use(source, target):
        source.add_aura(BarrageAura)

class XPotionOfDexterity(Skill):
    name = "X-Potion of Dexterity"
    animation_lock = LONG_DELAY
    cooldown = 270

    @staticmethod
    def use(source, target):
        source.add_aura(XPotionOfDexterityAura)

class HeavyShot(Skill):
    name = "Heavy Shot"
    animation_lock = GCD_DELAY
    tp_cost = 60

    @staticmethod
    def use(source, target):
        if random.random() < 0.2:
            source.add_aura(StraighterShotAura)
        target.add_damage(DamageHelper.calculate_damage(150, source)["potency"])

class StraightShot(Skill):
    name = "Straight Shot"
    animation_lock = GCD_DELAY
    tp_cost = 70

    @staticmethod
    def use(source, target):
        if source.has_aura(StraighterShotAura):
            source.remove_aura(StraighterShotAura)
            target.add_damage(DamageHelper.calculate_damage(140, source, { "guaranteed_critical": True })["potency"])
        else:
            target.add_damage(DamageHelper.calculate_damage(140, source)["potency"])
        source.add_aura(StraightShotAura)

class VenomousBite(Skill):
    name = "Venomous Bite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @staticmethod
    def use(source, target):
        target.add_damage(DamageHelper.calculate_damage(100, source)["potency"])
        target.add_aura(VenomousBiteAura, source)

class Windbite(Skill):
    name = "Windbite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @staticmethod
    def use(source, target):
        target.add_damage(DamageHelper.calculate_damage(60, source)["potency"])
        target.add_aura(WindbiteAura, source)

class FlamingArrow(Skill): 
    name = "Flaming Arrow"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_aura(FlamingArrowAura, source)

class BluntArrow(Skill):
    name = "Blunt Arrow"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_damage(DamageHelper.calculate_damage(50, source)["potency"])
        target.add_aura(SilenceAura, source)

class RepellingShot(Skill):
    name = "Repelling Shot"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_damage(DamageHelper.calculate_damage(80, source)["potency"])

class Bloodletter(Skill):
    name = "Bloodletter"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_damage(DamageHelper.calculate_damage(150, source)["potency"])

class Invigorate(Skill):
    name = "Invigorate"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        source.add_tp(400)

class AuraTimer:
    def __init__(self, duration=0, snapshot=[]):
        self.duration = duration
        self.snapshot = snapshot

class Actor:
    def __init__(self):
        self.auras = {} # key is (aura class, source actor)
        self.job = None
        self.tp = 1000
        self.damage = 0 # Damage inflicted on actor
        self.base_critical_hit_rate = 0.2

    def snapshot(self):
        return self.auras.keys()

    # Adds an aura to the actor.
    def add_aura(self, aura, source=None):
        if source is None:
            source = self

        aura_timer = None
        if aura.has_snapshot:
            aura_timer = AuraTimer(aura.duration, source.snapshot())
        else:
            aura_timer = AuraTimer(aura.duration)
        self.auras[(aura, source)] = aura_timer

    def remove_aura(self, aura, source=None):
        if source is None:
            source = self

        self.auras.pop((aura, source), None)

    def has_aura(self, aura, source=None):
        if source is None:
            source = self

        if (aura, source) in self.auras:
            return True
        else:
            return False

    def add_damage(self, potency):
        self.damage += potency

    def add_tp(self, value):
        if value >= 0:
            self.tp = min(self.tp + value, 1000)
        else:
            self.tp = max(self.tp - value, 0)

    def set_cooldown(self, aura, time):
        pass

class Simulation:
    def __init__(self):
        pass

source = Actor()
target = Actor()
RagingStrikes.use(source, target)
BloodForBlood.use(source, target)
StraightShot.use(source, target)
HeavyShot.use(source, target)
Windbite.use(source, target)
WindbiteAura.tick(source, target)
print target.damage