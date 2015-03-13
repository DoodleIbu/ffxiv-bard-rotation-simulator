import random

# Bard rotation potency calculator.
# TODO: fix lol code
#       support opening rotations
#       associate total potency dealt on enemy

class Timer:
    name = ""
    duration = 0
    snapshot = None

    def __init__(self, name, duration, snapshot=None):
        self.name = name
        self.duration = duration
        self.snapshot = snapshot

class TimerCollection:
    timers = []

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

class Job:
    pass

class Bard:

    def get_modified_potency(self, potency, timers, guaranteed_critical=False):
        critical_rate = 0.2
        potency_modifier = 1.0

        if timers is not None:
            if timers.has_timer("Straight Shot"):
                critical_rate += 0.1
            if timers.has_timer("Internal Release"):
                critical_rate += 0.1
            if timers.has_timer("Hawk's Eye"):
                potency_modifier *= 1.13 # Approximately?
            if timers.has_timer("Raging Strikes"):
                potency_modifier *= 1.20
            if timers.has_timer("Blood for Blood"):
                potency_modifier *= 1.10
            if timers.has_timer("X-Potion of Dexterity"):
                potency_modifier *= 1.11 # Approximately?

        critical = False
        if random.random() < critical_rate or guaranteed_critical:
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
        self.animation_lock = 0.8
        self.timers.set_timer("Hawk's Eye", 20)
        return True

    def raging_strikes(self):
        self.animation_lock = 0.8
        self.timers.set_timer("Raging Strikes", 20)
        return True

    def internal_release(self):
        self.animation_lock = 0.8
        self.timers.set_timer("Internal Release", 15)
        return True

    def barrage(self):
        self.animation_lock = 0.8
        self.timers.set_timer("Barrage", 10)
        return True

    def blood_for_blood(self):
        self.animation_lock = 0.8
        self.timers.set_timer("Blood for Blood", 20)
        return True

    def x_potion_of_dexterity(self):
        self.animation_lock = 1.2
        self.timers.set_timer("X-Potion of Dexterity", 15)
        return True

    def flaming_arrow(self):
        self.animation_lock = 0.8
        self.timers.set_timer("Flaming Arrow", 30, self.timers.create_snapshot())
        return True

    def blunt_arrow(self):
        self.animation_lock = 0.8
        self.total_potency += self.get_modified_normal_potency(50)
        return True

    def repelling_shot(self):
        self.animation_lock = 0.8
        self.total_potency += self.get_modified_normal_potency(80)
        return True

    def bloodletter(self):
        self.animation_lock = 0.8
        self.total_potency += self.get_modified_normal_potency(150)
        return True

    def invigorate(self):
        self.animation_lock = 0.8
        self.tp = min(self.tp + 400, 1000)
        return True

    def heavy_shot(self):
        if self.tp >= 60:
            self.tp -= 60
            self.animation_lock = 0.8
            self.total_potency += self.get_modified_normal_potency(150)
            if random.random() < 0.2:
                self.timers.set_timer("Straighter Shot", 10)
            return True
        return False

    def straight_shot(self):
        if self.tp >= 70:
            self.tp -= 70
            self.animation_lock = 0.8
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
            self.animation_lock = 0.8
            self.total_potency += self.get_modified_normal_potency(60)
            self.timers.set_timer("Windbite", 18, self.timers.create_snapshot())
            return True
        return False

    def venomous_bite(self):
        if self.tp >= 80:
            self.tp -= 80
            self.animation_lock = 0.8
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
            if straight_shot_timer.duration < 2.5:
                return True
            if windbite_timer is not None and windbite_timer.duration < 5 and straight_shot_timer.duration < 5:
                return True
            if venomous_bite_timer is not None and venomous_bite_timer.duration < 5 and straight_shot_timer.duration < 5:
                return True
            return False

        return True

    def should_refresh_windbite(self):
        windbite_timer = self.timers.get_timer("Windbite")
        if windbite_timer is not None:
            if windbite_timer.duration < 2.5:
                return True
            return False
        return True

    def should_refresh_venomous_bite(self):
        venomous_bite_timer = self.timers.get_timer("Venomous Bite")
        if venomous_bite_timer is not None:
            if venomous_bite_timer.duration < 2.5:
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
            "cooldown": 2.5,
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
            "cooldown": 3.04,
            "effects": auto_attack
        }
    }

    # States while attacking.
    total_potency = 0
    tp = 1000
    time = 0
    animation_lock = 0
    ability_cooldowns = {}
    misc_cooldowns = {}
    timers = TimerCollection()

    def __init__(self):
        for name, values in self.ABILITIES.iteritems():
            self.ability_cooldowns[name] = 0
        for name, values in self.MISC.iteritems():
            self.misc_cooldowns[name] = 0

    # Check buff duration, on GCD cooldown duration, and
    # misc cooldowns.
    # TODO: lol shitty code
    def process_event(self):
        time_passed = 10

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
        if self.can_use(name):
            success = self.ABILITIES[name]["effects"](self)
            if success:
                self.ability_cooldowns[name] = self.ABILITIES[name]["cooldown"]
    
    # USE EVERYTHING ASAP
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

            if self.can_use("Internal Release"):
                self.use("Internal Release")

            if self.can_use("Raging Strikes"):
                self.use("Raging Strikes")

            if self.can_use("Blood for Blood"):
                self.use("Blood for Blood")

            if self.can_use("Hawk's Eye"):
                self.use("Hawk's Eye")

            if self.can_use("Barrage"):
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

    # Parse the spoony bard.
    def parse(self, duration):
        while self.time < duration:
            self.act()
            self.process_event()

        return self.total_potency

sum_dps = 0
num_simulations = 1000

for i in xrange(num_simulations):
    bard = Bard()
    parse_length = 240
    potency = bard.parse(parse_length)
    damage_per_potency = 2.4888
    sum_dps += potency * damage_per_potency / parse_length

sum_dps /= num_simulations
print sum_dps
