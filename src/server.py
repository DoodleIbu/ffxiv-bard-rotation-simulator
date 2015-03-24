# Server-specific timers.
class Server:
    def __init__(self, actors):
        self.tick_timer = 0 # Time until next TP/MP/DoT tick
        self.actors = actors

    def tick(self):
        for actor in self.actors:
            actor.tick()
        self.tick_timer = 3

    def advance_time(self, time):
        self.tick_timer -= time
        if self.tick_timer <= 0:
            self.tick()

    def get_time_of_interest(self):
        return self.tick_timer
