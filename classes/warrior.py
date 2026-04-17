import random
import time

class Warrior:
    name = "Warrior"

    def __init__(self):
        self.skills = {}

    # ---------------------------------------------------------
    # BASIC ATTACKS
    # ---------------------------------------------------------
    def lunge(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = player.strength * 1.2
        crit = random.random() < 0.10
        damage = int(base * (2 if crit else 1))

        player.cooldown_until = time.time() + 1.5
        return damage, f"You lunge forward for {damage} damage!", crit

    def slash(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = player.strength
        crit = random.random() < 0.15
        damage = int(base * (2 if crit else 1))

        player.cooldown_until = time.time() + 1.2
        return damage, f"You slash the enemy for {damage} damage!", crit

    # ---------------------------------------------------------
    # DRAW ATTACK (stronger, slower)
    # ---------------------------------------------------------
    def draw(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = player.strength * 1.5
        crit = random.random() < 0.20
        damage = int(base * (2 if crit else 1))

        player.cooldown_until = time.time() + 2.0
        return damage, f"You draw back and strike hard for {damage} damage!", crit

    # ---------------------------------------------------------
    # RAGE SLASH (high crit chance)
    # ---------------------------------------------------------
    def rage_slash(self, player):
        if not player.can_act():
            return 0, "You are still recovering!", False

        base = player.strength * 1.3
        crit = random.random() < 0.35
        damage = int(base * (2 if crit else 1))

        player.cooldown_until = time.time() + 2.5
        return damage, f"You unleash a rage slash for {damage} damage!", crit

    # ---------------------------------------------------------
    # LEVEL UP GAINS
    # ---------------------------------------------------------
    def level_up(self, player):
        player.strength += 2
        player.constitution += 2

        player.max_hp = player.constitution * 10
        player.max_stamina = player.constitution * 5

        player.hp = player.max_hp
        player.stamina = player.max_stamina
