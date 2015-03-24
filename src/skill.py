import random
from damagehelper import *

SHORT_DELAY = 0.7
LONG_DELAY = 1.1
GCD_DELAY = 1.0

# Data on auras
class Aura:
    name = ""
    duration = 0
    has_snapshot = False

    @staticmethod
    def tick(source, target):
        pass

    @staticmethod
    def potency_modifier():
        return {}

class SilenceAura(Aura):
    name = "Silence"
    duration = 1 # Some moves may give the same aura but have different durations

class InternalReleaseAura(Aura):
    name = "Internal Release"
    duration = 15

    @staticmethod
    def potency_modifier():
        return {
            "critical_hit_rate_add": 0.10
        }

class BloodForBloodAura(Aura):
    name = "Blood for Blood"
    duration = 20

    @staticmethod
    def potency_modifier():
        return {
            "potency_multiply": 1.10
        }

class RagingStrikesAura(Aura):
    name = "Raging Strikes"
    duration = 20

    @staticmethod
    def potency_modifier():
        return {
            "potency_multiply": 1.20
        }

class HawksEyeAura(Aura):
    name = "Hawk's Eye"
    duration = 20

    @staticmethod
    def potency_modifier():
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
    def potency_modifier():
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
    def potency_modifier():
        return {
            "potency_multiply": 1.11 # about. Hawk's Eye also affects X-Pot bonuses (i.e. it's multiplicative)
        }

class FlamingArrowAura(Aura):
    name = "Flaming Arrow"
    duration = 30
    has_snapshot = True

    @staticmethod
    def tick(source, target):
        result = DamageHelper.calculate_dot_potency(30, source, target, FlamingArrowAura)
        target.add_potency(result["potency"])

class VenomousBiteAura(Aura):
    name = "Venomous Bite"
    duration = 18
    has_snapshot = True

    @staticmethod
    def tick(source, target):
        result = DamageHelper.calculate_dot_potency(35, source, target, VenomousBiteAura)
        target.add_potency(result["potency"])
        if result["critical_hit"] is True and random.random() < 0.5:
            source.set_cooldown(Bloodletter, 0)

class WindbiteAura(Aura):
    name = "Windbite"
    duration = 18
    has_snapshot = True

    @staticmethod
    def tick(source, target):
        result = DamageHelper.calculate_dot_potency(45, source, target, WindbiteAura)
        target.add_potency(result["potency"])
        if result["critical_hit"] is True and random.random() < 0.5:
            source.set_cooldown(Bloodletter, 0)

# Data on skills
class Skill:
    name = ""
    animation_lock = 0
    cooldown = 0
    tp_cost = 0
    is_off_gcd = False

    @staticmethod
    def use(source, target):
        pass

class InternalRelease(Skill):
    name = "Internal Release"
    animation_lock = SHORT_DELAY
    cooldown = 60
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        source.add_aura(InternalReleaseAura)

class BloodForBlood(Skill):
    name = "Blood for Blood"
    animation_lock = SHORT_DELAY
    cooldown = 80
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        source.add_aura(BloodForBloodAura)

class RagingStrikes(Skill):
    name = "Raging Strikes"
    animation_lock = SHORT_DELAY
    cooldown = 120
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        source.add_aura(RagingStrikesAura)

class HawksEye(Skill):
    name = "Hawk's Eye"
    animation_lock = SHORT_DELAY
    cooldown = 90
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        source.add_aura(HawksEyeAura)

class Barrage(Skill):
    name = "Barrage"
    animation_lock = SHORT_DELAY
    cooldown = 90
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        source.add_aura(BarrageAura)

class XPotionOfDexterity(Skill):
    name = "X-Potion of Dexterity"
    animation_lock = LONG_DELAY
    cooldown = 270
    is_off_gcd = True

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
        target.add_potency(DamageHelper.calculate_potency(150, source)["potency"])

class StraightShot(Skill):
    name = "Straight Shot"
    animation_lock = GCD_DELAY
    tp_cost = 70

    @staticmethod
    def use(source, target):
        if source.has_aura(StraighterShotAura):
            source.remove_aura(StraighterShotAura)
            target.add_potency(DamageHelper.calculate_potency(140, source, guaranteed_critical=True)["potency"])
        else:
            target.add_potency(DamageHelper.calculate_potency(140, source)["potency"])
        source.add_aura(StraightShotAura)

class VenomousBite(Skill):
    name = "Venomous Bite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(100, source)["potency"])
        target.add_aura(VenomousBiteAura, source)

class Windbite(Skill):
    name = "Windbite"
    animation_lock = GCD_DELAY
    tp_cost = 80

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(60, source)["potency"])
        target.add_aura(WindbiteAura, source)

class FlamingArrow(Skill): 
    name = "Flaming Arrow"
    animation_lock = SHORT_DELAY
    cooldown = 60
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        target.add_aura(FlamingArrowAura, source)

class BluntArrow(Skill):
    name = "Blunt Arrow"
    animation_lock = SHORT_DELAY
    cooldown = 30
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(50, source)["potency"])
        target.add_aura(SilenceAura, source)

class RepellingShot(Skill):
    name = "Repelling Shot"
    animation_lock = SHORT_DELAY
    cooldown = 30
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(80, source)["potency"])

class Bloodletter(Skill):
    name = "Bloodletter"
    animation_lock = SHORT_DELAY
    cooldown = 15
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(150, source)["potency"])

class Invigorate(Skill):
    name = "Invigorate"
    animation_lock = SHORT_DELAY
    cooldown = 120
    is_off_gcd = True

    @staticmethod
    def use(source, target):
        source.add_tp(400)

class AutoAttack(Skill):
    name = "Auto Attack"
    animation_lock = 0

    @staticmethod
    def use(source, target):
        auto_attacks = 1
        if source.has_aura(BarrageAura):
            auto_attacks = 3

        for i in xrange(0, auto_attacks):
            target.add_potency(DamageHelper.calculate_potency(88.7, source)["potency"])
