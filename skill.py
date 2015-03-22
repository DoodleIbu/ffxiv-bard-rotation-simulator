from aura import *
from damagehelper import *

SHORT_DELAY = 0.7
LONG_DELAY = 1.1
GCD_DELAY = 1.0

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
        target.add_potency(DamageHelper.calculate_potency(150, source)["potency"])

class StraightShot(Skill):
    name = "Straight Shot"
    animation_lock = GCD_DELAY
    tp_cost = 70

    @staticmethod
    def use(source, target):
        if source.has_aura(StraighterShotAura):
            source.remove_aura(StraighterShotAura)
            target.add_potency(DamageHelper.calculate_potency(140, source, { "guaranteed_critical": True })["potency"])
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

    @staticmethod
    def use(source, target):
        target.add_aura(FlamingArrowAura, source)

class BluntArrow(Skill):
    name = "Blunt Arrow"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(50, source)["potency"])
        target.add_aura(SilenceAura, source)

class RepellingShot(Skill):
    name = "Repelling Shot"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(80, source)["potency"])

class Bloodletter(Skill):
    name = "Bloodletter"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        target.add_potency(DamageHelper.calculate_potency(150, source)["potency"])

class Invigorate(Skill):
    name = "Invigorate"
    animation_lock = SHORT_DELAY

    @staticmethod
    def use(source, target):
        source.add_tp(400)