import random
from engine.skill import Skill
from engine.distance import Distance
from classes.baseclass import BaseClass

class Warrior(BaseClass):
    name = "Warrior"

    def __init__(self):
        self.weapon_damage = 2
        self.weapon_weight = 2
        self.rage_slash_rank = 1
        self.rage_slash_cost = 3

        self.skills = {
            "Lunge": Skill("Lunge"),
            "Slash": Skill("Slash"),
            "Draw": Skill("Draw"),
            "Rage Slash": Skill("Rage Slash")
        }

    def can_wield_weapon(self, player):
        return self.weapon_weight <= player.strength * 0.75

    def strength_modifier(self, player):
        return player.strength * 0.02

    def _compute_damage(self, base, player, skill):
        str_mod = self.strength_modifier(player)
        damage = base + str_mod

        # Damage variance ±10%
        damage *= random.uniform(0.9, 1.1)

        # Critical hits: 2% per skill level, capped at 25%
        crit_chance = min(0.25, skill.level * 0.02)
        crit = random.random() < crit_chance
        if crit:
            damage *= 1.5

        return max(0.0, damage), crit

    def basic_attack(self, player, attack_name):
        if not player.can_act():
            return 0.0, "You cannot act yet — still in cooldown.", False
        if not self.can_wield_weapon(player):
            return 0.0, "Your strength is too low to wield this weapon.", False
        if player.distance != Distance.MELEE:
            return 0.0, "You must be in melee distance to attack.", False

        player.set_cooldown(2)
        skill = self.skills[attack_name]
        if not skill.attempt():
            return 0.0, f"{attack_name} failed!", False

        damage, crit = self._compute_damage(1, player, skill)

        level_msg = None
        if skill.add_xp(0.02):
            level_msg = f"{attack_name} leveled up! Now level {skill.level}"

        if crit:
            msg = f"CRITICAL {attack_name} deals {damage:.2f} damage!"
        else:
            msg = f"{attack_name} deals {damage:.2f} damage!"

        if level_msg:
            msg += f" | {level_msg}"

        return damage, msg, crit

    def lunge(self, player):
        return self.basic_attack(player, "Lunge")

    def slash(self, player):
        return self.basic_attack(player, "Slash")

    def draw(self, player):
        return self.basic_attack(player, "Draw")

    def rage_slash(self, player):
        if not player.can_act():
            return 0.0, "You cannot act yet — still in cooldown.", False
        if not self.can_wield_weapon(player):
            return 0.0, "Your strength is too low to wield this weapon.", False
        if player.distance != Distance.MELEE:
            return 0.0, "You must be in melee distance to use Rage Slash.", False
        if player.stamina < self.rage_slash_cost:
            return 0.0, "Not enough stamina to perform Rage Slash.", False

        player.set_cooldown(4)
        skill = self.skills["Rage Slash"]
        if not skill.attempt():
            return 0.0, "Rage Slash failed!", False

        player.stamina -= self.rage_slash_cost

        base = self.weapon_damage + 3 * self.rage_slash_rank
        damage, crit = self._compute_damage(base, player, skill)

        level_msg = None
        if skill.add_xp(0.02):
            level_msg = f"Rage Slash leveled up! Now level {skill.level}"

        if crit:
            msg = f"CRITICAL Rage Slash hits for {damage:.2f} damage! (Stamina left: {player.stamina})"
        else:
            msg = f"Rage Slash hits for {damage:.2f} damage! (Stamina left: {player.stamina})"

        if level_msg:
            msg += f" | {level_msg}"

        return damage, msg, crit

    def level_up(self, player):
        player.strength += 2
        player.constitution += 1
