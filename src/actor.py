import sys
from skill import *
from timer import *

# Dumb slate for a character or enemy.
class Actor:
    def __init__(self, name):
        self.name = name
        self.cooldown_timers = {}
        self.aura_timers = {}
        self.gcd_timer = 0      # time until next GCD
        self.aa_timer = 0       # time until next auto attack
        self.animation_lock = 0 # time until animation lock is finished
        self.tp = 1000
        self.potency_dealt = {}
        self.potency_received = {}
        # Format:
        # {
        #     <actor>:
        #         {
        #             "potency": 500,
        #             "breakdown": {
        #                 <HeavyShot>: 250,
        #                 <StraightShot>: 250
        #             }
        #         }
        # }

        # Static parameters that sh1ould be passed into the actor
        self.base_critical_hit_rate = 0.197586
        self.aa_cooldown = 3.04
        self.gcd_cooldown = 2.45
        self.damage_per_potency = 2.4888

        # For time of interest purposes to check if a cooldown has been reset.
        self.check_now = True

    def snapshot(self):
        return [AuraTimer(aura_timer.cls, aura_timer.source) for aura_timer in self.aura_timers.values()]

    # Adds an aura to the actor.
    def add_aura(self, aura_cls, source=None):
        if source is None:
            source = self

        aura_timer = None
        if aura_cls.has_snapshot:
            aura_timer = AuraTimer(aura_cls, source, source.snapshot())
        else:
            aura_timer = AuraTimer(aura_cls, source)
        self.aura_timers[hash(aura_timer)] = aura_timer

    def remove_aura(self, aura_cls, source=None):
        if source is None:
            source = self

        identifier = AuraTimer.hash(aura_cls, source)
        if identifier in self.aura_timers:
            self.aura_timers.pop(identifier)

    def has_aura(self, aura_cls, source=None):
        if source is None:
            source = self

        identifier = AuraTimer.hash(aura_cls, source)
        if identifier in self.aura_timers:
            return True
        else:
            return False

    # Returns 0 if aura does not exist.
    def aura_duration(self, aura_cls, source=None):
        if source is None:
            source = self

        identifier = AuraTimer.hash(aura_cls, source)
        if identifier in self.aura_timers:
            return self.aura_timers[identifier].duration
        else:
            return 0

    def reset_cooldown(self, skill_cls):
        self.check_now = True
        if skill_cls in self.cooldown_timers:
            self.cooldown_timers.pop(skill_cls)

    # Currently assumes the actor has access to the skill.
    def cooldown_duration(self, skill_cls):
        if skill_cls in self.cooldown_timers:
            return self.cooldown_timers[skill_cls].duration
        else:
            return 0

    # Adds damage in terms of potency.
    def add_potency(self, args):
        source = args["source"]
        potency = args["potency"]
        critical_hit = args["critical_hit"]

        if source not in self.potency_received:
            self.potency_received[source] = {}
            self.potency_received[source]["potency"] = 0
            self.potency_received[source]["breakdown"] = {}
        self.potency_received[source]["potency"] += potency

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

        for _, aura_timer in self.aura_timers.iteritems():
            if aura_timer.duration < time:
                time = aura_timer.duration

        for _, cooldown_timer in self.cooldown_timers.iteritems():
            if cooldown_timer.duration < time:
                time = cooldown_timer.duration

        return time

    def advance_cooldowns(self, time):
        timers_to_remove = []
        for _, cooldown_timer in self.cooldown_timers.iteritems():
            cooldown_timer.duration -= time
            if cooldown_timer.duration <= 0:
                timers_to_remove.append(cooldown_timer.cls)

        for skill_cls in timers_to_remove:
            self.cooldown_timers.pop(skill_cls)

    def advance_auras(self, time):
        timers_to_remove = []
        for _, aura_timer in self.aura_timers.iteritems():
            aura_timer.duration -= time
            if aura_timer.duration <= 0:
                timers_to_remove.append(hash(aura_timer))

        for identifier in timers_to_remove:
            self.aura_timers.pop(identifier)

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
        for _, aura in self.aura_timers.iteritems():
            aura.cls.tick(aura.source, self)

    def use(self, skill_cls, target=None):
        if target is None:
            target = self

        if self.can_use(skill_cls):
            skill_cls.use(self, target)
            if skill_cls == AutoAttack:
                self.aa_timer = self.aa_cooldown
            elif skill_cls.is_off_gcd:
                self.animation_lock = skill_cls.animation_lock
                self.cooldown_timers[skill_cls] = CooldownTimer(skill_cls)
            else:
                self.add_tp(-1 * skill_cls.tp_cost)
                self.animation_lock = skill_cls.animation_lock
                self.gcd_timer = self.gcd_cooldown

    # Currently assumes the actor has access to the skill.
    def can_use(self, skill_cls):
        if skill_cls == AutoAttack:
            return self.aa_ready()

        if self.animation_lock <= 0:
            if skill_cls.is_off_gcd:
                return not skill_cls in self.cooldown_timers
            else:
                return self.gcd_ready() and self.tp >= skill_cls.tp_cost

    def gcd_ready(self):
        return self.gcd_timer <= 0

    def aa_ready(self):
        return self.aa_timer <= 0
