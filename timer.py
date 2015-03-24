class AuraTimer:
    def __init__(self, cls, source, snapshot=[]):
        self.cls = cls
        self.source = source
        self.duration = cls.duration
        self.snapshot = snapshot

    def __hash__(self):
        return AuraTimer.hash(self.cls, self.source)

    @staticmethod
    def hash(cls, source):
        return hash(cls.name) ^ hash(source.name)
