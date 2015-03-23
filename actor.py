import sys
from skill import *

class AuraTimer:
    def __init__(self, duration=0, snapshot=[]):
        self.duration = duration
        self.snapshot = snapshot

# Dumb slate for a character or enemy.
class Actor:
    def __init__(self, job):
        self.job = job

        # Initialize cooldown durations on actor
        self.cooldowns = {}
        if self.job is not None:
            for skill in job.skills:
                self.cooldowns[skill] = 0

        self.auras = {}         # keys are (aura class, source actor)
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

    # Returns 0 if aura does not exist.
    def aura_duration(self, aura, source=None):
        if source is None:
            source = self

        if (aura, source) in self.auras:
            return self.auras[(aura, source)].duration
        else:
            return 0

    def cooldown_duration(self, skill):
        if skill in self.cooldowns:
            return self.cooldowns[skill]
        else:
            return sys.maxint

    # Adds damage in terms of potency.
    def add_potency(self, potency):
        self.potency += potency

    def add_tp(self, value):
        if value >= 0:
            self.tp = min(self.tp + value, 1000)
        else:
            self.tp = max(self.tp + value, 0)

    def set_cooldown(self, skill, time):
        if time == 0:
            self.check_now = True

        if skill in self.cooldowns:
            self.cooldowns[skill] = time

    # Gets the amount of time that needs to pass until something important happens.
    def get_time_of_interest(self):
        if self.check_now:
            self.check_now = False
            return 0

        times = [sys.maxint, self.gcd_timer, self.aa_timer, self.animation_lock] \
              + [aura.duration for aura in self.auras.values()] \
              + self.cooldowns.values()
        times = [time for time in times if time != 0]

        return min(times)

    # Advances time.
    def advance_time(self, time):
        self.gcd_timer = max(self.gcd_timer - time, 0)
        self.aa_timer = max(self.aa_timer - time, 0)
        self.animation_lock = max(self.animation_lock - time, 0)

        auras_to_remove = []
        for aura_tuple, aura_timer in self.auras.iteritems():
            aura_timer.duration = max(aura_timer.duration - time, 0)
            if aura_timer.duration == 0:
                auras_to_remove.append((aura_tuple[0], aura_tuple[1]))

        for aura_to_remove in auras_to_remove:
            del self.auras[aura_to_remove]

        for cooldown in self.cooldowns.keys():
            self.cooldowns[cooldown] = max(self.cooldowns[cooldown] - time, 0)

    def use(self, skill, target=None):
        if target is None:
            target = self

        if skill == AutoAttack:
            skill.use(self, target)
            self.aa_timer = self.aa_cooldown

        elif self.can_use(skill):
            skill.use(self, target)
            self.animation_lock = skill.animation_lock
            if skill.is_off_gcd:
                self.cooldowns[skill] = skill.cooldown
            else:
                self.add_tp(-1 * skill.tp_cost)
                self.gcd_timer = self.gcd_cooldown

    # Currently assumes the actor has access to the skill.
    def can_use(self, skill):
        if self.animation_lock == 0:
            if skill.is_off_gcd:
                return self.cooldowns[skill] == 0
            else:
                return self.gcd_timer == 0 and self.tp >= skill.tp_cost

    # Includes DoT ticks and TP ticks
    def tick(self):
        self.add_tp(60)
        for aura_tuple in self.auras.keys():
            aura_tuple[0].tick(aura_tuple[1], self)

    def gcd_ready(self):
        return self.gcd_timer == 0

    def aa_ready(self):
        return self.aa_timer == 0