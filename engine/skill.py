import random

class Skill:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0.0
        self.xp_required = 10.0  # doubles each level

    def success_chance(self):
        # 40% base + 10% per level, capped at 95%
        chance = 0.40 + 0.10 * (self.level - 1)
        return min(chance, 0.95)

    def attempt(self):
        return random.random() <= self.success_chance()

    def add_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.xp >= self.xp_required:
            self.xp -= self.xp_required
            self.level += 1
            self.xp_required *= 2
            leveled_up = True
        return leveled_up
