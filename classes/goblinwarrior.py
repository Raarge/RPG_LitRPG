import random
from engine.skill import Skill
from engine.distance import Distance
from engine.monster import Monster

class GoblinWarrior(Monster):
    def __init__(self, level, is_boss=False):
        super().__init__(level, is_boss)
        self.weapon_damage = 2
        self.weapon_weight = 2
        self.power_swipe_rank = 1
        self.power_swipe_cost = 3

        self.skills = {
            "Lunge": Skill("Lunge"),
            "Slash": Skill("Slash"),
            "Draw": Skill("Draw"),
            "Power Swipe": Skill("Power Swipe")
        }

    def strength_modifier(self):
        return self.strength * 0.02

    def _compute_damage(self, base, skill):
        damage = base + self.strength_modifier()
        damage *= random.uniform(0.9, 1.1)

        crit_chance = min(0.25, skill.level * 0.02)
        crit = random.random() < crit_chance
        if crit:
            damage *= 1.5

        return max(0.0, damage), crit

    def gain_skill_xp(self, skill_name):
        skill = self.skills[skill_name]
        leveled = skill.add_xp(0.02)
        if leveled:
            return f"Goblin's {skill_name} leveled up!"
        return None

    def basic_attack(self, attack_name):
        if not self.can_act():
            return 0.0, "Goblin is still in cooldown.", False
        if self.distance != Distance.MELEE:
            return 0.0, "Goblin is not in melee range.", False

        self.set_cooldown(2)
        skill = self.skills[attack_name]
        if not skill.attempt():
            return 0.0, f"Goblin's {attack_name} failed!", False

        damage, crit = self._compute_damage(1, skill)

        level_msg = None
        if skill.add_xp(0.02):
            level_msg = f"Goblin's {attack_name} leveled up!"

        if crit:
            msg = f"Goblin's CRITICAL {attack_name} hits for {damage:.2f} damage!"
        else:
            msg = f"Goblin uses {attack_name} for {damage:.2f} damage!"

        if level_msg:
            msg += f" | {level_msg}"

        return damage, msg, crit

    def lunge(self):
        return self.basic_attack("Lunge")

    def slash(self):
        return self.basic_attack("Slash")

    def draw(self):
        return self.basic_attack("Draw")

    def power_swipe(self):
        if not self.can_act():
            return 0.0, "Goblin is still in cooldown.", False
        if self.distance != Distance.MELEE:
            return 0.0, "Goblin is not in melee range.", False
        if self.stamina < self.power_swipe_cost:
            return 0.0, "Goblin does not have enough stamina!", False

        self.set_cooldown(4)
        skill = self.skills["Power Swipe"]
        if not skill.attempt():
            return 0.0, "Goblin's Power Swipe failed!", False

        self.stamina -= self.power_swipe_cost

        base = self.weapon_damage + 3 * self.power_swipe_rank
        damage, crit = self._compute_damage(base, skill)

        level_msg = None
        if skill.add_xp(0.02):
            level_msg = f"Goblin's Power Swipe leveled up!"

        if crit:
            msg = f"Goblin's CRITICAL Power Swipe hits for {damage:.2f} damage! (Stamina left: {self.stamina})"
        else:
            msg = f"Goblin uses Power Swipe for {damage:.2f} damage! (Stamina left: {self.stamina})"

        if level_msg:
            msg += f" | {level_msg}"

        return damage, msg, crit

    def choose_action(self):
        # Low HP behavior
        if self.hp <= 0.25 * self.max_hp:
            roll = random.random()
            if roll < 0.5:
                # Try to retreat if possible
                if self.distance > Distance.RANGED:
                    return self.retreat
            elif roll < 0.75:
                # Try strongest attack
                return self.power_swipe

        # Normal behavior
        if self.distance != Distance.MELEE:
            return self.advance

        actions = [self.lunge, self.slash, self.draw, self.power_swipe]
        return random.choice(actions)
