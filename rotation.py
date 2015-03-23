import sys

from skill import *

class Rotation:
    @staticmethod
    def get_time_of_interest(source):
        return sys.maxint

    @staticmethod
    def use_skill(source, target):
        pass

class BardRotation(Rotation):
    @staticmethod
    def get_time_of_interest(source):
        return sys.maxint

    @staticmethod
    def use_skill(source, target):
        source.use_skill(HeavyShot, target)
