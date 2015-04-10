import sys
from skill import *

class Rotation:
    def get_time_of_interest(self, server, player):
        return sys.maxint

    def use_skill(self, server, player, enemy):
        pass

class BardRotation(Rotation):

    def __init__(self):
        self.opener_state = 0

    def _opener(self, server, player, enemy):
        return

    def get_time_of_interest(self, server, player):
        time_until_barrage = player.aa_timer - (10 - player.aa_cooldown * 3)
        if time_until_barrage > 0:
            return time_until_barrage
        else:
            return sys.maxint

    def use_skill(self, server, player, enemy):
        self._opener(server, player, enemy)

        if player.aa_ready():
            player.use(AutoAttack, enemy)

        if player.gcd_ready():

            # Should refresh Straight Shot?
            if player.can_use(StraightShot):
                if not player.has_aura(StraightShotAura):
                    return player.use(StraightShot, enemy)
                elif player.aura_duration(StraightShotAura) < player.gcd_cooldown:
                    return player.use(StraightShot, enemy)
                elif enemy.has_aura(WindbiteAura, player) and enemy.aura_duration(WindbiteAura, player) < player.gcd_cooldown * 2 and \
                   player.aura_duration(StraightShotAura) < player.gcd_cooldown * 2:
                    return player.use(StraightShot, enemy)
                elif enemy.has_aura(VenomousBiteAura, player) and enemy.aura_duration(VenomousBiteAura, player) < player.gcd_cooldown * 2 and \
                   player.aura_duration(StraightShotAura) < player.gcd_cooldown * 2:
                    return player.use(StraightShot, enemy)

            # Should refresh DoTs?
            if player.can_use(Windbite):
                if not enemy.has_aura(WindbiteAura, player):
                    return player.use(Windbite, enemy)
                elif enemy.aura_duration(WindbiteAura, player) < player.gcd_cooldown:
                    return player.use(Windbite, enemy)

            if player.can_use(VenomousBite):
                if not enemy.has_aura(VenomousBiteAura, player):
                    return player.use(VenomousBite, enemy)
                elif enemy.aura_duration(VenomousBiteAura, player) < player.gcd_cooldown:
                    return player.use(VenomousBite, enemy)

            if player.can_use(StraightShot):
                if player.has_aura(StraighterShotAura):
                    return player.use(StraightShot, enemy)

            if player.can_use(HeavyShot):
                return player.use(HeavyShot, enemy)

        if player.gcd_timer >= LONG_DELAY:
            if player.can_use(XPotionOfDexterity):
                return player.use(XPotionOfDexterity)

        if player.gcd_timer >= SHORT_DELAY:

            if player.can_use(Invigorate):
                if (player.tp <= 600 and server.tick_timer > player.gcd_timer) or \
                    player.tp <= 540:
                    return player.use(Invigorate)

            use_internal_release = enemy.aura_duration(WindbiteAura, player) < 15 \
                               and enemy.aura_duration(VenomousBiteAura, player) < 15
            if player.can_use(InternalRelease) and use_internal_release:
                return player.use(InternalRelease)

            if player.can_use(RagingStrikes):
                return player.use(RagingStrikes)

            if player.cooldown_duration(Barrage) < 8:
                if player.can_use(BloodForBlood) and player.can_use(HawksEye):
                    return player.use(BloodForBlood)

                if player.can_use(HawksEye):
                    return player.use(HawksEye)

            if player.can_use(Barrage) and player.aa_timer < 10 - player.aa_cooldown * 3:
                return player.use(Barrage)

            if player.can_use(FlamingArrow):
                return player.use(FlamingArrow, enemy)

            if player.can_use(Bloodletter):
                return player.use(Bloodletter, enemy)

            if player.can_use(RepellingShot):
                return player.use(RepellingShot, enemy)

            if player.can_use(BluntArrow):
                return player.use(BluntArrow, enemy)
