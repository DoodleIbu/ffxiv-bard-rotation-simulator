import random
import sys

# Bard rotation potency calculator.
# TODO: fix lol code
#       support opening rotations
#       associate total potency dealt on enemy
#       support mid-GCD activation of buffs, especially Barrage and Bloodletter spam
GCD = 2.45
AUTO_ATTACK_DELAY = 3.04
CRITICAL_HIT_RATE = 0.197586

class Timer:
    def __init__(self, name, duration, snapshot=None):
        self.name = name
        self.duration = duration
        self.snapshot = snapshot

class TimerCollection:
    def get_timer(self, name):
        for timer in self.timers:
            if timer.name == name:
                return timer
        return None

    def delete_timer(self, name):
        self.timers = [timer for timer in self.timers if timer.name != name]

    def set_timer(self, name, duration, snapshot=None):
        self.delete_timer(name)
        self.timers.append(Timer(name, duration, snapshot))

    def has_timer(self, name):
        return self.get_timer(name) is not None

    # Creates a snapshot.
    def create_snapshot(self):
        new_timers = TimerCollection()
        for timer in self.timers:
            new_timers.set_timer(timer.name, timer.duration)
        return new_timers

    def __iter__(self):
        return iter(self.timers)

    def __init__(self):
        self.timers = []

class Job:
    pass

class Bard:

    def get_modified_potency(self, potency, timers, guaranteed_critical=False):
        critical_hit_rate = CRITICAL_HIT_RATE
        potency_modifier = 1.0

        if timers is not None:
            if timers.has_timer("Straight Shot"):
                critical_hit_rate += 0.1
            if timers.has_timer("Internal Release"):
                critical_hit_rate += 0.1
            if timers.has_timer("Hawk's Eye"):
                potency_modifier *= 1.13 # Approximately?
            if timers.has_timer("Raging Strikes"):
                potency_modifier *= 1.20
            if timers.has_timer("Blood for Blood"):
                potency_modifier *= 1.10
            if timers.has_timer("X-Potion of Dexterity"):
                potency_modifier *= 1.11 # Approximately?

        critical = False
        if random.random() < critical_hit_rate or guaranteed_critical:
            critical = True

        total_potency = (potency \
                       + potency * critical * 0.5) \
                       * potency_modifier
        return total_potency, critical

    def get_modified_normal_potency(self, potency, guaranteed_critical=False):
        return self.get_modified_potency(potency, self.timers)[0]

    def get_modified_dot_potency(self, potency, snapshot):
        return self.get_modified_potency(potency, snapshot)

    def hawks_eye(self):
        self.animation_lock = 0.7
        self.timers.set_timer("Hawk's Eye", 20)
        return True

    def raging_strikes(self):
        self.animation_lock = 0.7
        self.timers.set_timer("Raging Strikes", 20)
        return True

    def internal_release(self):
        self.animation_lock = 0.7
        self.timers.set_timer("Internal Release", 15)
        return True

    def barrage(self):
        self.animation_lock = 0.7
        self.timers.set_timer("Barrage", 10)
        return True

    def blood_for_blood(self):
        self.animation_lock = 0.7
        self.timers.set_timer("Blood for Blood", 20)
        return True

    def x_potion_of_dexterity(self):
        self.animation_lock = 1.1
        self.timers.set_timer("X-Potion of Dexterity", 15)
        return True

    def flaming_arrow(self):
        self.animation_lock = 0.7
        self.timers.set_timer("Flaming Arrow", 30, self.timers.create_snapshot())
        return True

    def blunt_arrow(self):
        self.animation_lock = 0.7
        self.total_potency += self.get_modified_normal_potency(50)
        return True

    def repelling_shot(self):
        self.animation_lock = 0.7
        self.total_potency += self.get_modified_normal_potency(80)
        return True

    def bloodletter(self):
        self.animation_lock = 0.7
        self.total_potency += self.get_modified_normal_potency(150)
        return True

    def invigorate(self):
        self.animation_lock = 0.7
        self.tp = min(self.tp + 400, 1000)
        return True

    def heavy_shot(self):
        if self.tp >= 60:
            self.tp -= 60
            self.animation_lock = 1.0
            self.total_potency += self.get_modified_normal_potency(150)
            if random.random() < 0.2:
                self.timers.set_timer("Straighter Shot", 10)
            return True
        return False

    def straight_shot(self):
        if self.tp >= 70:
            self.tp -= 70
            self.animation_lock = 1.0
            if self.timers.has_timer("Straighter Shot"):
                self.total_potency += self.get_modified_normal_potency(140, True)
                self.timers.delete_timer("Straighter Shot")
            else:
                self.total_potency += self.get_modified_normal_potency(140)

            self.timers.set_timer("Straight Shot", 20)
            return True
        return False

    def windbite(self):
        if self.tp >= 80:
            self.tp -= 80
            self.animation_lock = 1.0
            self.total_potency += self.get_modified_normal_potency(60)
            self.timers.set_timer("Windbite", 18, self.timers.create_snapshot())
            return True
        return False

    def venomous_bite(self):
        if self.tp >= 80:
            self.tp -= 80
            self.animation_lock = 1.0
            self.total_potency += self.get_modified_normal_potency(100)
            self.timers.set_timer("Venomous Bite", 18, self.timers.create_snapshot())
            return True
        return False

    def tp_tick(self):
        self.tp = min(self.tp + 60, 1000)
        return True

    def dot_tick(self):
        venomous_bite_timer = self.timers.get_timer("Venomous Bite")
        windbite_timer = self.timers.get_timer("Windbite")
        flaming_arrow_timer = self.timers.get_timer("Flaming Arrow")

        if venomous_bite_timer is not None:
            potency, critical = self.get_modified_dot_potency(35, venomous_bite_timer.snapshot)
            self.total_potency += potency
            if critical and random.random() < 0.5:
                self.ability_cooldowns["Bloodletter"] = 0
        if windbite_timer is not None:
            potency, critical = self.get_modified_dot_potency(45, windbite_timer.snapshot)
            self.total_potency += potency
            if critical and random.random() < 0.5:
                self.ability_cooldowns["Bloodletter"] = 0
        if flaming_arrow_timer is not None:
            potency, critical = self.get_modified_dot_potency(45, flaming_arrow_timer.snapshot)
            self.total_potency += potency

        return True

    def auto_attack(self):
        self.total_potency += self.get_modified_normal_potency(88.7)
        if self.timers.has_timer("Barrage"):
            self.total_potency += self.get_modified_normal_potency(88.7)
            self.total_potency += self.get_modified_normal_potency(88.7)
        return True

    def should_refresh_straight_shot(self):
        straight_shot_timer = self.timers.get_timer("Straight Shot")
        windbite_timer = self.timers.get_timer("Windbite")
        venomous_bite_timer = self.timers.get_timer("Venomous Bite")

        if straight_shot_timer is not None:
            if straight_shot_timer.duration < GCD:
                return True
            if windbite_timer is not None and windbite_timer.duration < 2 * GCD and straight_shot_timer.duration < 2 * GCD:
                return True
            if venomous_bite_timer is not None and venomous_bite_timer.duration < 2 * GCD and straight_shot_timer.duration < 2 * GCD:
                return True
            return False

        return True

    def should_refresh_windbite(self):
        windbite_timer = self.timers.get_timer("Windbite")
        if windbite_timer is not None:
            if windbite_timer.duration < GCD:
                return True
            return False
        return True

    def should_refresh_venomous_bite(self):
        venomous_bite_timer = self.timers.get_timer("Venomous Bite")
        if venomous_bite_timer is not None:
            if venomous_bite_timer.duration < GCD:
                return True
            return False
        return True

    # Choose a GCD to use.
    def gcd(self):
        if self.should_refresh_straight_shot():
            return self.straight_shot()
        elif self.should_refresh_windbite():
            return self.windbite()
        elif self.should_refresh_venomous_bite():
            return self.venomous_bite()
        elif self.timers.has_timer("Straighter Shot"):
            return self.straight_shot()
        else:
            return self.heavy_shot()

        return False

    ABILITIES = {
        "GCD": {
            "cooldown": GCD,
            "effects": gcd
        },
        "Hawk's Eye": {
            "cooldown": 80,
            "effects": hawks_eye
        },
        "Raging Strikes": {
            "cooldown": 120,
            "effects": raging_strikes
        },
        "Internal Release": {
            "cooldown": 60,
            "effects": internal_release
        },
        "Barrage": {
            "cooldown": 90,
            "effects": barrage
        },
        "Blood for Blood": {
            "cooldown": 80,
            "effects": blood_for_blood
        },
        "X-Potion of Dexterity": {
            "cooldown": 270,
            "effects": x_potion_of_dexterity
        },
        "Blunt Arrow": {
            "cooldown": 30,
            "effects": blunt_arrow
        },
        "Repelling Shot": {
            "cooldown": 30,
            "effects": repelling_shot
        },
        "Bloodletter": {
            "cooldown": 15,
            "effects": bloodletter
        },
        "Flaming Arrow": {
            "cooldown": 60,
            "effects": flaming_arrow
        },
        "Invigorate": {
            "cooldown": 120,
            "effects": invigorate
        }
    }

    MISC = {
        "TP Tick": {
            "cooldown": 3,
            "effects": tp_tick
        },
        "DoT Tick": {
            "cooldown": 3,
            "effects": dot_tick
        },
        "Auto Attack": {
            "cooldown": AUTO_ATTACK_DELAY,
            "effects": auto_attack
        }
    }

    def __init__(self):
        self.total_potency = 0
        self.tp = 1000
        self.time = 0
        self.animation_lock = 0
        self.ability_cooldowns = {}
        self.misc_cooldowns = {}
        self.timers = TimerCollection()
        for name, values in self.ABILITIES.iteritems():
            self.ability_cooldowns[name] = 0
        for name, values in self.MISC.iteritems():
            self.misc_cooldowns[name] = 0

    # Check buff duration, on GCD cooldown duration, and
    # misc cooldowns.
    # TODO: lol shitty code
    def process_event(self):
        time_passed = sys.maxint

        # Animation lock
        if self.animation_lock != 0:
            if self.animation_lock < time_passed:
                time_passed = self.animation_lock

        # Expired buffs/dots
        for timer in self.timers:
            if timer.duration != 0:
                if timer.duration < time_passed:
                    time_passed = timer.duration

        # Off GCD
        for name, duration in self.ability_cooldowns.iteritems():
            if duration != 0:
                if duration < time_passed:
                    time_passed = duration

        # Misc cooldowns
        for name, duration in self.misc_cooldowns.iteritems():
            if duration != 0:
                if duration < time_passed:
                    time_passed = duration

        # ========================================================

        # Go through each timer again and decrement by time_passed.
        if self.animation_lock > 0:
            self.animation_lock = max(self.animation_lock - time_passed, 0)

        timers_to_delete = []
        for timer in self.timers:
            if timer.duration > 0:
                timer.duration = max(timer.duration - time_passed, 0)
                if timer.duration == 0:
                    timers_to_delete.append(timer.name)

        for timer_to_delete in timers_to_delete:
            self.timers.delete_timer(timer_to_delete)

        for name, _ in self.ability_cooldowns.iteritems():
            if self.ability_cooldowns[name] > 0:
                self.ability_cooldowns[name] = max(self.ability_cooldowns[name] - time_passed, 0)

        for name, _ in self.misc_cooldowns.iteritems():
            if self.misc_cooldowns[name] > 0:
                self.misc_cooldowns[name] = max(self.misc_cooldowns[name] - time_passed, 0)

        self.time += time_passed

    def use_misc(self):
        for name, _ in self.misc_cooldowns.iteritems():
            if self.misc_cooldowns[name] == 0:
                success = self.MISC[name]["effects"](self)
                if success:
                    self.misc_cooldowns[name] = self.MISC[name]["cooldown"]

    def can_use(self, name):
        if self.animation_lock == 0 and self.ability_cooldowns[name] == 0:
            return True
        return False

    def use(self, name):
        # print "%s -- %.3f" % (name, self.ability_cooldowns["GCD"])
        # Straight shot, etc. Need to clean this up
        if name == "Straight Shot" and self.can_use("GCD"):
            success = self.straight_shot()
            if success:
                self.ability_cooldowns["GCD"] = self.ABILITIES["GCD"]["cooldown"]
            return success
        elif name == "Heavy Shot" and self.can_use("GCD"):
            success = self.heavy_shot()
            if success:
                self.ability_cooldowns["GCD"] = self.ABILITIES["GCD"]["cooldown"]
            return success
        elif name == "Windbite" and self.can_use("GCD"):
            success = self.windbite()
            if success:
                self.ability_cooldowns["GCD"] = self.ABILITIES["GCD"]["cooldown"]
            return success
        elif name == "Venomous Bite" and self.can_use("GCD"):
            success = self.venomous_bite()
            if success:
                self.ability_cooldowns["GCD"] = self.ABILITIES["GCD"]["cooldown"]
            return success
        elif name in self.ABILITIES and self.can_use(name):
            success = self.ABILITIES[name]["effects"](self)
            if success:
                self.ability_cooldowns[name] = self.ABILITIES[name]["cooldown"]
            return success

        return False

    def use_abilities(self):
        if self.can_use("GCD"):
            self.use("GCD")

        # Long animations
        if self.ability_cooldowns["GCD"] >= 1.2:
            if self.can_use("X-Potion of Dexterity"):
                self.use("X-Potion of Dexterity")

        # Regular animations
        if self.ability_cooldowns["GCD"] >= 0.8:
            if self.can_use("Invigorate") and self.tp <= 600 and \
               self.misc_cooldowns["TP Tick"] > self.ability_cooldowns["GCD"]:
                self.use("Invigorate")

            # Time internal release so that both dots get the critical bonus.
            windbite_timer = self.timers.get_timer("Windbite")
            venomous_bite_timer = self.timers.get_timer("Venomous Bite")
            use_internal_release = False
            if (windbite_timer is None or windbite_timer.duration < 15) and \
               (venomous_bite_timer is None or venomous_bite_timer.duration < 15):
               use_internal_release = True

            if self.can_use("Internal Release") and use_internal_release:
                self.use("Internal Release")

            if self.can_use("Raging Strikes"):
                self.use("Raging Strikes")

            if self.ability_cooldowns["Barrage"] < 8:
                if self.can_use("Blood for Blood") and self.can_use("Hawk's Eye"):
                    self.use("Blood for Blood")

                if self.can_use("Hawk's Eye"):
                    self.use("Hawk's Eye")

            if self.can_use("Barrage") and self.misc_cooldowns["Auto Attack"] < 10 - (AUTO_ATTACK_DELAY * 3):
                self.use("Barrage")

            if self.can_use("Flaming Arrow"):
                self.use("Flaming Arrow")

            if self.can_use("Bloodletter"):
                self.use("Bloodletter")

            if self.can_use("Repelling Shot"):
                self.use("Repelling Shot")

            if self.can_use("Blunt Arrow"):
                self.use("Blunt Arrow")

    # Execute action(s).
    def act(self):
        self.use_misc()
        self.use_abilities()

    # Krietor's opener
    # Notation: (skill name, optional)
    def opener(self):
        opener = [("Hawk's Eye", False),
                  ("Raging Strikes", False),
                  ("Bloodletter", False),
                  ("Straight Shot", False),
                  ("Blood for Blood", False),
                  ("Internal Release", False),
                  ("Windbite", False),
                  ("X-Potion of Dexterity", False),
                  ("Barrage", False),
                  ("Venomous Bite", False),
                  ("Flaming Arrow", False),
                  ("Repelling Shot", False),
                  ("Heavy Shot", False),
                  ("Blunt Arrow", False),
                  ("Heavy Shot", False),
                  ("Heavy Shot", False),
                  ("Windbite", False),
                  ("Venomous Bite", False)]

        for ability in opener:
            name = ability[0]
            optional = ability[1]

            if optional:
                self.use_misc()
                self.use(name)
                self.process_event()
            else:
                success = False
                while not success:
                    self.use_misc()
                    success = self.use(name)
                    self.process_event()

    # Lazy opener
    def opener2(self):
        opener = [("Straight Shot", False),
                  ("Hawk's Eye", False),
                  ("Internal Release", False),
                  ("Windbite", False),
                  ("Blood for Blood", False),
                  ("Raging Strikes", False),
                  ("Venomous Bite", False),
                  ("X-Potion of Dexterity", False),
                  ("Heavy Shot", False),
                  ("Barrage", False),
                  ("Bloodletter", False),
                  ("Heavy Shot", False),
                  ("Flaming Arrow", False),
                  ("Repelling Shot", False),
                  ("Heavy Shot", False),
                  ("Blunt Arrow", False),
                  ("Heavy Shot", False),
                  ("Windbite", False),
                  ("Venomous Bite", False)]

        for ability in opener:
            name = ability[0]
            optional = ability[1]

            if optional:
                self.use_misc()
                self.use(name)
                self.process_event()
            else:
                success = False
                while not success:
                    self.use_misc()
                    success = self.use(name)
                    self.process_event()

    # Parse the spoony bard.
    def parse(self, duration, blah=True):
        if blah:
            self.opener()
        else:
            self.opener2()

        while self.time < duration:
            self.act()
            self.process_event()

        return self.total_potency

# Krietor's opener
sum_dps = 0
num_simulations = 1000

for i in xrange(num_simulations):
    bard = Bard()
    parse_length = 241.4
    potency = bard.parse(parse_length)
    damage_per_potency = 2.4888
    sum_dps += potency * damage_per_potency / (parse_length - 1.4)

sum_dps /= num_simulations
print sum_dps

# Lazy opener
sum_dps = 0
num_simulations = 1000

for i in xrange(num_simulations):
    bard = Bard()
    parse_length = 240
    potency = bard.parse(parse_length, False)
    damage_per_potency = 2.4888
    sum_dps += potency * damage_per_potency / 240

sum_dps /= num_simulations
print sum_dps

