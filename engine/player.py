import time
import json
import os

class Player:
    def __init__(self, class_obj):
        self.class_obj = class_obj

        # Base stats
        self.strength = 10
        self.dexterity = 10
        self.constitution = 10
        self.intelligence = 10
        self.wisdom = 10
        self.dispell = 0

        # Derived pools
        self.max_hp = self.constitution * 10
        self.hp = self.max_hp

        self.max_stamina = self.constitution * 5
        self.stamina = self.max_stamina

        # XP & Level
        self.level = 1
        self.xp = 0
        self.xp_required = 100

        # Combat
        self.distance = 1
        self.cooldown_until = 0

        # Training points
        self.training_points = 0

        # Gold
        self.gold = 0

        self.weapon_damage = 2   # basic sword


    # ---------------------------------------------------------
    # STATS DICT FOR UI
    # ---------------------------------------------------------
    def stats(self):
        return {
            "STR": self.strength,
            "DEX": self.dexterity,
            "CON": self.constitution,
            "INT": self.intelligence,
            "WIS": self.wisdom,
            "DISPELL": self.dispell
        }

    # ---------------------------------------------------------
    # CAN ACT?
    # ---------------------------------------------------------
    def can_act(self):
        return time.time() >= self.cooldown_until

    # ---------------------------------------------------------
    # LEVELING
    # ---------------------------------------------------------
    def gain_xp(self, amount):
        self.xp += amount
        leveled = False

        while self.xp >= self.xp_required:
            self.xp -= self.xp_required
            self.level += 1
            self.xp_required = int(self.xp_required * 1.5)

            # Class-specific stat gains
            self.class_obj.level_up(self)

            # Update HP/Stamina pools
            self.update_pools_on_level()

            # Training points per level
            self.training_points += 2

            leveled = True

        return leveled

    def update_pools_on_level(self):
        self.max_hp = self.constitution * 10
        self.max_stamina = self.constitution * 5
        self.hp = self.max_hp
        self.stamina = self.max_stamina

    # ---------------------------------------------------------
    # TRAINING POINT ALLOCATION
    # ---------------------------------------------------------
    def allocate_stat(self, stat_name):
        if self.training_points <= 0:
            return False

        self.training_points -= 1

        if stat_name == "STR":
            self.strength += 1
        elif stat_name == "DEX":
            self.dexterity += 1
        elif stat_name == "CON":
            self.constitution += 1
            self.update_pools_on_level()
        elif stat_name == "INT":
            self.intelligence += 1
        elif stat_name == "WIS":
            self.wisdom += 1
        elif stat_name == "DISPELL":
            self.dispell += 1

        return True

    # ---------------------------------------------------------
    # SAVE / LOAD
    # ---------------------------------------------------------
    def from_dict(self, data):
        # Core progression
        self.level = data.get("level", 1)
        self.xp = data.get("xp", 0)
        self.xp_required = data.get("xp_required", 100)

        # Stats (fallbacks ensure old saves load safely)
        self.strength = data.get("strength", 5)
        self.dexterity = data.get("dexterity", 5)
        self.constitution = data.get("constitution", 5)
        self.intelligence = data.get("intelligence", 5)
        self.wisdom = data.get("wisdom", 5)
        self.dispell = data.get("dispell", 0)
        self.weapon_damage = data.get("weapon_damage", 2)


        # Derived pools
        self.max_hp = data.get("max_hp", self.constitution * 10)
        self.hp = data.get("hp", self.max_hp)

        self.max_stamina = data.get("max_stamina", self.constitution * 5)
        self.stamina = data.get("stamina", self.max_stamina)

        # Training points (new system)
        self.training_points = data.get("training_points", 0)

        # Gold (if present)
        self.gold = data.get("gold", 0)

    def to_dict(self):
        return {
            "class": self.class_obj.name,
            "level": self.level,
            "xp": self.xp,
            "xp_required": self.xp_required,

            # Stats
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "dispell": self.dispell,

            # Pools
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,

            # Training points
            "training_points": self.training_points,

            "weapon_damage": self.weapon_damage,


            # Gold (if you use it)
            "gold": self.gold

            
        }


    def save(self):
        data = self.to_dict()
        filename = f"{self.class_obj.name}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        return f"Saved to {filename}"

    def load(self):
        filename = f"{self.class_obj.name}.json"
        if not os.path.exists(filename):
            return "No save file found."

        with open(filename, "r") as f:
            data = json.load(f)

        self.from_dict(data)
        return "Game loaded."

    def regen(self, in_combat):
        # HP regeneration: slow, halved during combat
        hp_regen = self.max_hp / 360
        if in_combat:
            hp_regen *= 0.5
        self.hp = min(self.max_hp, self.hp + hp_regen)

        # Stamina regeneration: faster, NOT halved in combat
        stam_regen = self.max_stamina / 180
        self.stamina = min(self.max_stamina, self.stamina + stam_regen)

    # ---------------------------------------------------------
    # DISTANCE-BASED MOVEMENT
    # ---------------------------------------------------------
    def advance(self):
        if self.distance <= 1:
            return "You are already in melee range."

        self.distance -= 1
        return f"You advance to distance {self.distance}."

    def retreat(self):
        if self.distance >= 3:
            return "You cannot retreat any further."

        self.distance += 1
        return f"You retreat to distance {self.distance}."

    # ---------------------------------------------------------
    # FLEE ATTEMPT
    # ---------------------------------------------------------
    def flee(self, monster):
        import random

        # Base flee chance
        chance = 0.35

        # Dexterity helps fleeing
        chance += (self.dexterity * 0.005)

        if random.random() < chance:
            return "You successfully fled the battle!"
        else:
            return "You failed to flee!"

    def use_potion(self):
        # If you want potions to be an inventory item, add inventory logic later.
        # For now, treat it as a simple heal action.

        if self.hp >= self.max_hp:
            return "You are already at full health."

        heal_amount = int(self.max_hp * 0.35)  # Heals 35% of max HP
        self.hp = min(self.max_hp, self.hp + heal_amount)

        return f"You drink a potion and heal {heal_amount} HP."
