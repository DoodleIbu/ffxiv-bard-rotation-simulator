import random

# Helper class to calculate potency.
class DamageHelper:

    @staticmethod
    def _calculate_potency(potency, source, auras, **kwargs):
        potency_modifier = 1.0
        critical_hit_rate = source.base_critical_hit_rate # Might be snapshotted, but it's pretty pointless to simulate that

        for aura in auras:
            cls = aura[0]
            result = cls.potency_modifier()
            if "potency_multiply" in result:
                potency_modifier *= result["potency_multiply"]
            if "critical_hit_rate_add" in result:
                critical_hit_rate += result["critical_hit_rate_add"]

        critical_hit = False
        if random.random() < critical_hit_rate or kwargs.get("guaranteed_critical", False) is True:
            critical_hit = True

        return {
            "potency": potency * potency_modifier * (1 + critical_hit * 0.5),
            "critical_hit": critical_hit
        }

    @staticmethod
    def calculate_potency(potency, source, **kwargs):
        return DamageHelper._calculate_potency(potency, source, source.auras.keys(), **kwargs)

    @staticmethod
    def calculate_dot_potency(potency, source, target, aura, **kwargs):
        return DamageHelper._calculate_potency(potency, source, target.auras[(aura, source)].snapshot, **kwargs)
