import random
from classes.goblinwarrior import GoblinWarrior

def generate_monster(player_level):
    roll = random.randint(1, 100)
    if roll <= 85:
        return GoblinWarrior(player_level)
    elif roll <= 97:
        return GoblinWarrior(player_level + 1)
    elif roll <= 99:
        return GoblinWarrior(player_level + 2)
    else:
        boss_level = player_level if random.random() < 0.5 else player_level + 1
        return GoblinWarrior(boss_level, is_boss=True)

def generate_loot(monster):
    import random
    xp = monster.level * 5
    gold = random.randint(monster.level * 1, monster.level * 3)

    rare_items = [
        "Goblin Tooth",
        "Rusty Dagger",
        "Torn Cloth",
        "Goblin Ear",
        "Small Gemstone"
    ]

    rare_drop = None
    if random.random() <= 0.05:  # 5% chance
        if random.random() <= 0.2:  # 1% overall for gemstone
            rare_drop = "Small Gemstone"
        else:
            rare_drop = random.choice(rare_items[:-1])

    return xp, gold, rare_drop
