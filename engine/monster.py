from engine.combatant import Combatant

class Monster(Combatant):
    def __init__(self, level, is_boss=False):
        super().__init__()
        self.level = level
        self.is_boss = is_boss
        self.difficulty_multiplier = 1.5 if is_boss else 1.0

        base_stat = 5 * self.difficulty_multiplier
        self.strength = int(base_stat)
        self.dexterity = int(base_stat)
        self.constitution = int(base_stat)

        self.max_stamina = self.constitution * 5
        self.stamina = self.max_stamina

        # Level-scaled HP
        self.max_hp = int((self.level * 5 + 20) * self.difficulty_multiplier)
        self.hp = self.max_hp

    def __repr__(self):
        if self.is_boss:
            return f"Goblin Boss (Lvl {self.level})"
        return f"Goblin Warrior (Lvl {self.level})"
