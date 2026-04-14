import time
from engine.distance import Distance

class Combatant:
    def __init__(self):
        self.distance = Distance.RANGED
        self.cooldown_until = 0.0

    def can_act(self):
        return time.time() >= self.cooldown_until

    def set_cooldown(self, seconds):
        self.cooldown_until = time.time() + seconds

    def advance(self):
        if not self.can_act():
            return "You cannot act yet — still in cooldown."
        if self.distance < Distance.MELEE:
            self.distance += 1
            self.set_cooldown(1)
            return f"Advanced to {Distance.names[self.distance]}"
        return "Already at melee distance."

    def retreat(self):
        if not self.can_act():
            return "You cannot act yet — still in cooldown."
        if self.distance > Distance.RANGED:
            self.distance -= 1
            self.set_cooldown(1)
            return f"Retreated to {Distance.names[self.distance]}"
        return "Already at maximum range."
