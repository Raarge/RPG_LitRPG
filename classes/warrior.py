import random
import time

class Warrior:
    name = "Warrior"

    def __init__(self):
        # Expecting something like:
        # self.skills = {
        #     "Lunge": Skill(...),
        #     "Slash": Skill(...),
        #     ...
        # }
        self.skills = {}

    # -----------------------------
    # INTERNAL: DAMAGE CALC
    # -----------------------------
    def _compute_base_damage(self, player, power_multiplier: float = 1.0) -> float:
        """
        Core physical damage formula:
        - 1 base damage
        - + STR modifier (0.02 per STR)
        - + weapon damage (if present on player)
        - scaled by power_multiplier (for heavier skills)
        """
        str_mod = player.strength * 0.02
        weapon_damage = getattr(player, "weapon_damage", 0)

        base = (1 + str_mod + weapon_damage) * power_multiplier
        return base

    def _final_damage(self, base: float, crit_chance: float) -> (int, bool):
        """
        Apply ±10% variance and crit.
        """
        # ±10% variance
        variance = random.uniform(0.9, 1.1)
        dmg = base * variance

        # Crit
        is_crit = random.random() < crit_chance
        if is_crit:
            dmg *= 2

        return max(1, int(dmg)), is_crit

    def _spend_stamina_and_cooldown(self, player, stamina_cost: int, cooldown: float):
        """
        Spend stamina if your engine supports it, then set cooldown.
        If you don't use stamina yet, you can ignore the cost or
        just ensure the attribute exists on Player.
        """
        if hasattr(player, "stamina"):
            player.stamina = max(0, player.stamina - stamina_cost)

        player.cooldown_until = time.time() + cooldown

    # -----------------------------
    # BASIC ATTACKS
    # -----------------------------
    def lunge(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = self._compute_base_damage(player, power_multiplier=1.0)
        damage, crit = self._final_damage(base, crit_chance=0.10)

        self._spend_stamina_and_cooldown(player, stamina_cost=3, cooldown=1.5)

        msg = f"You lunge forward for {damage} damage!"
        if crit:
            msg += " (Critical hit!)"

        return damage, msg, crit

    def slash(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = self._compute_base_damage(player, power_multiplier=1.1)
        damage, crit = self._final_damage(base, crit_chance=0.15)

        self._spend_stamina_and_cooldown(player, stamina_cost=4, cooldown=1.7)

        msg = f"You slash the enemy for {damage} damage!"
        if crit:
            msg += " (Critical hit!)"

        return damage, msg, crit

    # -----------------------------
    # HEAVIER ATTACKS
    # -----------------------------
    def draw(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = self._compute_base_damage(player, power_multiplier=1.3)
        damage, crit = self._final_damage(base, crit_chance=0.20)

        self._spend_stamina_and_cooldown(player, stamina_cost=6, cooldown=2.0)

        msg = f"You draw back and strike hard for {damage} damage!"
        if crit:
            msg += " (Critical hit!)"

        return damage, msg, crit

    def rage_slash(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = self._compute_base_damage(player, power_multiplier=1.2)
        damage, crit = self._final_damage(base, crit_chance=0.35)

        self._spend_stamina_and_cooldown(player, stamina_cost=8, cooldown=2.5)

        msg = f"You unleash a rage slash for {damage} damage!"
        if crit:
            msg += " (Critical hit!)"

        return damage, msg, crit

    # -----------------------------
    # LEVEL UP GAINS
    # -----------------------------
    def level_up(self, player):
        # Simple, punchy Warrior scaling
        player.strength += 2
        player.constitution += 2

        # Recompute derived stats
        player.max_hp = player.constitution * 10
        player.max_stamina = player.constitution * 5

        player.hp = player.max_hp
        player.stamina = player.max_stamina
