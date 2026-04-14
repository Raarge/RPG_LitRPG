import time
from engine.combatant import Combatant
from engine.distance import Distance
import json
import os

class Human:
    def __init__(self):
        self.strength = 5
        self.dexterity = 5
        self.constitution = 5
        self.intelligence = 5
        self.wisdom = 5
        self.dispell = 5

    def stats(self):
        return {
            "STR": self.strength,
            "DEX": self.dexterity,
            "CON": self.constitution,
            "INT": self.intelligence,
            "WIS": self.wisdom,
            "DISPELL": self.dispell
        }

class Player(Human, Combatant):
    def __init__(self, class_obj):
        Human.__init__(self)
        Combatant.__init__(self)
        self.class_obj = class_obj

        self.level = 1
        self.xp = 0.0
        self.xp_required = 100.0

        self.gold = 0
        self.potions = 10
        self.potion_cooldown_until = 0.0

        self._init_pools()

    def _init_pools(self):
        self.max_hp = self.constitution * 10
        self.hp = self.max_hp
        self.max_stamina = self.constitution * 5
        self.stamina = self.max_stamina

    def update_pools_on_level(self):
        old_max_hp = self.max_hp
        self.max_hp = self.constitution * 10
        delta_hp = self.max_hp - old_max_hp
        self.hp = min(self.max_hp, self.hp + max(0, delta_hp))

        old_max_stam = self.max_stamina
        self.max_stamina = self.constitution * 5
        delta_stam = self.max_stamina - old_max_stam
        self.stamina = min(self.max_stamina, self.stamina + max(0, delta_stam))

    def gain_xp(self, amount):
        self.xp += amount
        leveled = False
        while self.xp >= self.xp_required:
            self.xp -= self.xp_required
            self.level += 1
            self.xp_required *= 1.5
            self.class_obj.level_up(self)
            self.update_pools_on_level()
            leveled = True
        return leveled

    def regen(self, in_combat: bool):
        # --- Health regeneration ---
        # Full heal in 30 minutes (1800s) with 5s ticks => 360 ticks
        base_hp = self.max_hp / 360.0
        hp_amount = base_hp / 2.0 if in_combat else base_hp

        if self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + hp_amount)

        # --- Stamina regeneration ---
        # Same 30-minute full regen, but NEVER halved in combat
        base_stam = self.max_stamina / 360.0

        if self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + base_stam)


    def can_use_potion(self):
        return time.time() >= self.potion_cooldown_until

    def use_potion(self):
        if self.potions <= 0:
            return "You have no potions left."
        if not self.can_use_potion():
            return "You cannot use a potion yet."
        if self.hp >= self.max_hp:
            return "You are already at full health."

        self.potions -= 1
        self.potion_cooldown_until = time.time() + 5  # 5s cooldown
        heal_amount = int(self.max_hp * 0.30)
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + heal_amount)
        actual_heal = int(self.hp - old_hp)
        return f"You drink a potion and recover {actual_heal} HP."

    def flee(self, monster=None):
        from random import random
        if not self.can_act():
            return "You cannot flee — still in cooldown."

        base_chance = {
            Distance.RANGED: 0.90,
            Distance.POLE:   0.70,
            Distance.MELEE:  0.50
        }[self.distance]
        dex_bonus = self.dexterity * 0.01
        flee_chance = min(base_chance + dex_bonus, 0.95)

        roll = random()
        if roll <= flee_chance:
            return "You successfully fled the battle!"
        self.set_cooldown(2)
        return "You failed to flee!"

    def to_dict(self):
        return {
            "class": self.class_obj.name,
            "level": self.level,
            "xp": self.xp,
            "xp_required": self.xp_required,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "gold": self.gold,
            "distance": self.distance,
            "cooldown_until": self.cooldown_until,
            "stats": self.stats(),
            "skills": {
                name: {
                    "level": skill.level,
                    "xp": skill.xp,
                    "xp_required": skill.xp_required
            }
            for name, skill in self.class_obj.skills.items()
        }
    }


    def from_dict(self, data):
        self.level = data["level"]
        self.xp = data["xp"]
        self.xp_required = data["xp_required"]
        self.hp = data["hp"]
        self.max_hp = data["max_hp"]
        self.stamina = data["stamina"]
        self.max_stamina = data["max_stamina"]
        self.gold = data["gold"]
        self.distance = data["distance"]
        self.cooldown_until = data["cooldown_until"]

        # Restore stats
        for key, value in data["stats"].items():
            setattr(self, key.lower(), value)

        # Restore skills
        for name, skill_data in data["skills"].items():
            skill = self.class_obj.skills[name]
            skill.level = skill_data["level"]
            skill.xp = skill_data["xp"]
            skill.xp_required = skill_data["xp_required"]

    def save(self):
        data = self.to_dict()
        filename = f"{self.class_obj.name}.json"
        path = os.path.join(os.getcwd(), filename)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        return f"Game saved to {filename}"


    def load(self):
        filename = f"{self.class_obj.name}.json"
        path = os.path.join(os.getcwd(), filename)

        if not os.path.exists(path):
            return "No save file found."

        with open(path, "r") as f:
            data = json.load(f)

        self.from_dict(data)
        return "Game loaded successfully."

