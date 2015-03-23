import sys
from skill import *

SHORT_DELAY = 0.7
LONG_DELAY = 1.1
GCD_DELAY = 1.0

class Rotation:
    @staticmethod
    def get_time_of_interest(simulation, player):
        return sys.maxint

    @staticmethod
    def use_skill(simulation, player, enemy):
        pass

class BardRotation(Rotation):
    @staticmethod
    def get_time_of_interest(simulation, player):
        return sys.maxint

    # TODO: Add opener
    @staticmethod
    def use_skill(simulation, player, enemy):
        if player.aa_ready():
            player.use(AutoAttack, enemy)

        if player.gcd_ready():

            # Should refresh Straight Shot?
            if player.can_use(StraightShot):
                if not player.has_aura(StraightShotAura):
                    player.use(StraightShot, enemy)
                elif enemy.has_aura(WindbiteAura, player) and enemy.aura_duration(WindbiteAura, player) < player.gcd_cooldown * 2 and \
                   player.aura_duration(StraightShotAura) < player.gcd_cooldown * 2:
                    player.use(StraightShot, enemy)
                elif enemy.has_aura(VenomousBiteAura, player) and enemy.aura_duration(VenomousBiteAura, player) < player.gcd_cooldown * 2 and \
                   player.aura_duration(StraightShotAura) < player.gcd_cooldown * 2:
                    player.use(StraightShot, enemy)

            # Should refresh DoTs?
            if player.can_use(Windbite):
                if not enemy.has_aura(WindbiteAura, player):
                    player.use(Windbite, enemy)
                elif enemy.aura_duration(WindbiteAura, player) < player.gcd_cooldown:
                    player.use(Windbite, enemy)

            if player.can_use(VenomousBite):
                if not enemy.has_aura(VenomousBiteAura, player):
                    player.use(VenomousBite, enemy)
                elif enemy.aura_duration(VenomousBiteAura, player) < player.gcd_cooldown:
                    player.use(VenomousBite, enemy)

            if player.has_aura(StraighterShotAura):
                player.use(StraightShot, enemy)

            player.use(HeavyShot, enemy)

        if player.gcd_timer >= LONG_DELAY:
            if player.can_use(XPotionOfDexterity):
                player.use(XPotionOfDexterity)

        if player.gcd_timer >= SHORT_DELAY:

            if player.can_use(Invigorate) and (player.tp <= 600 and simulation.tick_timer > player.gcd_timer) or \
               player.tp <= 540:
                player.use(Invigorate)

            use_internal_release = enemy.aura_duration(WindbiteAura, player) < 15 \
                               and enemy.aura_duration(VenomousBiteAura, player) < 15

            if player.can_use(InternalRelease) and use_internal_release:
                player.use(InternalRelease)

            if player.can_use(RagingStrikes):
                player.use(RagingStrikes)

            if player.cooldown_duration(Barrage) < 8:
                if player.can_use(BloodForBlood) and player.can_use(HawksEye):
                    player.use(BloodForBlood)

                if player.can_use(HawksEye):
                    player.use(HawksEye)

            if player.can_use(Barrage) and player.aa_timer < 10 - player.aa_cooldown * 3:
                player.use(Barrage)

            if player.can_use(FlamingArrow):
                player.use(FlamingArrow, enemy)

            if player.can_use(Bloodletter):
                player.use(Bloodletter, enemy)

            if player.can_use(RepellingShot):
                player.use(RepellingShot, enemy)

            if player.can_use(BluntArrow):
                player.use(BluntArrow, enemy)
