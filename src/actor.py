import sys
from skill import *
from timer import *

# Dumb slate for a character or enemy.
class Actor:
    def __init__(self, name):
        self.name = name
        self.cooldowns = {}
        self.auras = {}
        self.gcd_timer = 0      # time until next GCD
        self.aa_timer = 0       # time until next auto attack
        self.animation_lock = 0 # time until animation lock is finished
        self.tp = 1000
        self.potency = 0 # Damage inflicted on actor in terms of potency.
                         # Actual damage = self.potency * self.damage_per_potency

        # Static parameters that should be passed into the actor
        self.base_critical_hit_rate = 0.197586
        self.aa_cooldown = 3.04
        self.gcd_cooldown = 2.45
        self.damage_per_potency = 2.4888 # TODO: associate potency damage on enemies with source

        # For time of interest purposes to check if a cooldown has been reset.
        self.check_now = True

    def snapshot(self):
        return [AuraTimer(aura.cls, aura.source) for aura in self.auras.values()]

    # Adds an aura to the actor.
    def add_aura(self, aura, source=None):
        if source is None:
            source = self

        aura_timer = None
        if aura.has_snapshot:
            aura_timer = AuraTimer(aura, source, source.snapshot())
        else:
            aura_timer = AuraTimer(aura, source)
        self.auras[hash(aura_timer)] = aura_timer

    def remove_aura(self, aura, source=None):
        if source is None:
            source = self

        identifier = AuraTimer.hash(aura, source)
        self.auras.pop(identifier)

    def has_aura(self, aura, source=None):
        if source is None:
            source = self

        identifier = AuraTimer.hash(aura, source)
        if identifier in self.auras:
            return True
        else:
            return False

    # Returns 0 if aura does not exist.
    def aura_duration(self, aura, source=None):
        if source is None:
            source = self

        identifier = AuraTimer.hash(aura, source)
        if identifier in self.auras:
            return self.auras[identifier].duration
        else:
            return 0

    def reset_cooldown(self, skill):
        self.check_now = True
        if skill in self.cooldowns:
            self.cooldowns.pop(skill)

    # Currently assumes the actor has access to the skill.
    def cooldown_duration(self, skill):
        if skill in self.cooldowns:
            return self.cooldowns[skill].duration
        else:
            return 0

    # Adds damage in terms of potency.
    def add_potency(self, potency):
        self.potency += potency

    def add_tp(self, value):
        if value >= 0:
            self.tp = min(self.tp + value, 1000)
        else:
            self.tp = max(self.tp + value, 0)

    # Gets the amount of time that needs to pass until something important happens.
    def get_time_of_interest(self):
        if self.check_now:
            self.check_now = False
            return 0

        time = sys.maxint
        if self.gcd_timer < time and self.gcd_timer > 0:
            time = self.gcd_timer
        if self.aa_timer < time and self.aa_timer > 0:
            time = self.aa_timer
        if self.animation_lock < time and self.animation_lock > 0:
            time = self.animation_lock

        for _, aura in self.auras.iteritems():
            if aura.duration < time:
                time = aura.duration

        for _, cooldown in self.cooldowns.iteritems():
            if cooldown.duration < time:
                time = cooldown.duration

        return time

    def advance_cooldowns(self, time):
        cooldowns_to_remove = []
        for _, cooldown_timer in self.cooldowns.iteritems():
            cooldown_timer.duration -= time
            if cooldown_timer.duration <= 0:
                cooldowns_to_remove.append(cooldown_timer.cls)

        for skill in cooldowns_to_remove:
            self.cooldowns.pop(skill)

    def advance_auras(self, time):
        auras_to_remove = []
        for _, aura_timer in self.auras.iteritems():
            aura_timer.duration -= time
            if aura_timer.duration <= 0:
                auras_to_remove.append(hash(aura_timer))

        for aura in auras_to_remove:
            self.auras.pop(aura)

    # Advances time.
    def advance_time(self, time):
        self.gcd_timer -= time
        self.aa_timer -= time
        self.animation_lock -= time
        self.advance_auras(time)
        self.advance_cooldowns(time)

    # Includes DoT ticks and TP ticks
    def tick(self):
        self.add_tp(60)
        for _, aura in self.auras.iteritems():
            aura.cls.tick(aura.source, self)

    def use(self, skill, target=None):
        if target is None:
            target = self

        if self.can_use(skill):
            skill.use(self, target)
            if skill == AutoAttack:
                self.aa_timer = self.aa_cooldown
            elif skill.is_off_gcd:
                self.animation_lock = skill.animation_lock
                self.cooldowns[skill] = CooldownTimer(skill)
            else:
                self.add_tp(-1 * skill.tp_cost)
                self.animation_lock = skill.animation_lock
                self.gcd_timer = self.gcd_cooldown

    # Currently assumes the actor has access to the skill.
    def can_use(self, skill):
        if skill == AutoAttack:
            return self.aa_ready()

        if self.animation_lock <= 0:
            if skill.is_off_gcd:
                return not skill in self.cooldowns
            else:
                return self.gcd_ready() and self.tp >= skill.tp_cost

    def gcd_ready(self):
        return self.gcd_timer <= 0

    def aa_ready(self):
        return self.aa_timer <= 0
