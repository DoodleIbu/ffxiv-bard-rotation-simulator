import sys
from skill import *

# http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# TODO: clean up parameters?
class Rotation:
    def get_time_of_interest(self, server, player):
        return sys.maxint

    def use_skill(self, server, player, enemy):
        pass

class BardRotation(Rotation):

    STATE = enum("OPENER", "ROTATION")
    OPENER_STATE = enum("HE", "RAS", "BL", "SS", "B4B", "IR", "WB1", "XP", "BAR", "VB1",
                        "HS1", "HS2", "HS3", "WB2", "VB2", "END")

    def __init__(self):
        self.state = BardRotation.STATE.OPENER
        self.opener_state = BardRotation.OPENER_STATE.HE

    def get_time_of_interest(self, server, player):
        time_until_barrage = player.aa_timer - (10 - player.aa_cooldown * 3)
        if time_until_barrage > 0:
            return time_until_barrage
        else:
            return sys.maxint

    def _opener_next_state(self):
        self.opener_state += 1

    # Each state currently consists of a mini rotation.
    # Could probably clean this up a bit.
    def _opener(self, server, player, enemy):
        if player.aa_ready() and self.opener_state >= BardRotation.OPENER_STATE.BL:
            player.use(AutoAttack, enemy)

        if self.opener_state == BardRotation.OPENER_STATE.HE:
            if player.can_use(HawksEye):
                self._opener_next_state()
                return player.use(HawksEye)

        elif self.opener_state == BardRotation.OPENER_STATE.RAS:
            if player.can_use(RagingStrikes):
                self._opener_next_state()
                return player.use(RagingStrikes)

        elif self.opener_state == BardRotation.OPENER_STATE.BL:
            if player.can_use(Bloodletter):
                self._opener_next_state()
                return player.use(Bloodletter, enemy)

        elif self.opener_state == BardRotation.OPENER_STATE.SS:
            if player.can_use(StraightShot):
                self._opener_next_state()
                return player.use(StraightShot, enemy)

        elif self.opener_state == BardRotation.OPENER_STATE.B4B:
            if player.can_use(BloodForBlood):
                self._opener_next_state()
                return player.use(BloodForBlood)

        elif self.opener_state == BardRotation.OPENER_STATE.IR:
            if player.can_use(InternalRelease):
                self._opener_next_state()
                return player.use(InternalRelease)

        elif self.opener_state == BardRotation.OPENER_STATE.WB1:
            if player.can_use(Windbite):
                self._opener_next_state()
                return player.use(Windbite, enemy)

        elif self.opener_state == BardRotation.OPENER_STATE.XP:
            if player.can_use(XPotionOfDexterity):
                self._opener_next_state()
                return player.use(XPotionOfDexterity)

        elif self.opener_state == BardRotation.OPENER_STATE.BAR:
            if player.can_use(Barrage):
                self._opener_next_state()
                return player.use(Barrage)

        elif self.opener_state == BardRotation.OPENER_STATE.VB1:
            if player.can_use(VenomousBite):
                self._opener_next_state()
                return player.use(VenomousBite, enemy)

        # TODO: Could condense the three Heavy Shot states to one state.
        elif self.opener_state == BardRotation.OPENER_STATE.HS1:
            if player.can_use(HeavyShot):
                self._opener_next_state()
                return player.use(HeavyShot, enemy)

            if player.gcd_timer >= SHORT_DELAY:
                if player.can_use(Bloodletter):
                    return player.use(Bloodletter, enemy)
                if player.can_use(FlamingArrow):
                    return player.use(FlamingArrow, enemy)
                if player.can_use(RepellingShot):
                    return player.use(RepellingShot, enemy)
                if player.can_use(BluntArrow):
                    return player.use(BluntArrow, enemy)

        # Start weaving Bloodletters here.
        elif self.opener_state == BardRotation.OPENER_STATE.HS2:
            if player.has_aura(StraighterShotAura):
                if player.can_use(StraightShot):
                    self._opener_next_state()
                    return player.use(StraightShot, enemy)
            elif player.can_use(HeavyShot):
                self._opener_next_state()
                return player.use(HeavyShot, enemy)

            if player.gcd_timer >= SHORT_DELAY:
                if player.can_use(Bloodletter):
                    return player.use(Bloodletter, enemy)
                if player.can_use(FlamingArrow):
                    return player.use(FlamingArrow, enemy)
                if player.can_use(RepellingShot):
                    return player.use(RepellingShot, enemy)
                if player.can_use(BluntArrow):
                    return player.use(BluntArrow, enemy)

        elif self.opener_state == BardRotation.OPENER_STATE.HS3:
            if player.has_aura(StraighterShotAura):
                if player.can_use(StraightShot):
                    self._opener_next_state()
                    return player.use(StraightShot, enemy)
            elif player.can_use(HeavyShot):
                self._opener_next_state()
                return player.use(HeavyShot, enemy)

            if player.gcd_timer >= SHORT_DELAY:
                if player.can_use(Bloodletter):
                    return player.use(Bloodletter, enemy)
                if player.can_use(FlamingArrow):
                    return player.use(FlamingArrow, enemy)
                if player.can_use(RepellingShot):
                    return player.use(RepellingShot, enemy)
                if player.can_use(BluntArrow):
                    return player.use(BluntArrow, enemy)

        elif self.opener_state == BardRotation.OPENER_STATE.WB2:
            if player.can_use(Windbite):
                self._opener_next_state()
                return player.use(Windbite, enemy)

            if player.gcd_timer >= SHORT_DELAY:
                if player.can_use(Bloodletter):
                    return player.use(Bloodletter, enemy)

        elif self.opener_state == BardRotation.OPENER_STATE.VB2:
            if player.can_use(VenomousBite):
                self._opener_next_state()
                self.state = BardRotation.STATE.ROTATION
                return player.use(VenomousBite, enemy)

            if player.gcd_timer >= SHORT_DELAY:
                if player.can_use(Bloodletter):
                    return player.use(Bloodletter, enemy)

    def _rotation(self, server, player, enemy):
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

            if player.can_use(InternalRelease):
                if enemy.aura_duration(WindbiteAura, player) < 15 and enemy.aura_duration(VenomousBiteAura, player) < 15:
                    return player.use(InternalRelease)

            if player.can_use(RagingStrikes):
                return player.use(RagingStrikes)

            if player.cooldown_duration(Barrage) < 8:
                # HE > B4B
                if player.can_use(HawksEye):
                    return player.use(HawksEye)

                if player.can_use(BloodForBlood) and not player.can_use(HawksEye):
                    return player.use(BloodForBlood)

            if player.can_use(Barrage):
                if player.aa_timer < 10 - player.aa_cooldown * 3:
                    return player.use(Barrage)

            if player.can_use(FlamingArrow):
                return player.use(FlamingArrow, enemy)

            if player.can_use(Bloodletter):
                return player.use(Bloodletter, enemy)

            if player.can_use(RepellingShot):
                return player.use(RepellingShot, enemy)

            if player.can_use(BluntArrow):
                return player.use(BluntArrow, enemy)

    def use_skill(self, server, player, enemy):
        if self.state == BardRotation.STATE.OPENER:
            self._opener(server, player, enemy)
        elif self.state == BardRotation.STATE.ROTATION:
            self._rotation(server, player, enemy)
