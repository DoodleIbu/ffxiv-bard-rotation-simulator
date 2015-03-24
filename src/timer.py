class AuraTimer:
    def __init__(self, cls, source, snapshot=[]):
        self.cls = cls
        self.duration = cls.duration
        self.source = source
        self.snapshot = snapshot

    def __hash__(self):
        return AuraTimer.hash(self.cls, self.source)

    @staticmethod
    def hash(cls, source):
        return hash(cls.name) ^ hash(source.name)

# Not really needed, but adding for consistency
class CooldownTimer:
    def __init__(self, cls):
        self.cls = cls
        self.duration = cls.cooldown

    def __hash__(self):
        return CooldownTimer.hash(self.cls)

    @staticmethod
    def hash(cls):
        return hash(cls.name)
