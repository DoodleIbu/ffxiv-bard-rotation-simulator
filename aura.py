import random
from damagehelper import *

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
    duration = 15

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
            "potency_multiply": 1.11 # about
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
