import tkinter as tk
from engine.player import Player
from classes.warrior import Warrior
from engine.generator import generate_monster, generate_loot
from ui.gameui import GameUI


def main():
    player_class = Warrior()
    player = Player(player_class)
    monster = generate_monster(player.level)

    root = tk.Tk()

    state = {
        "player": player,
        "monster": monster,
        "in_combat": True
    }

    # ---------------------------------------------------------
    # MONSTER AI (ROUNDTIME-BASED)
    # ---------------------------------------------------------
    def monster_ai_tick():
        m = state["monster"]
        p = state["player"]

        if state["in_combat"] and m and m.hp > 0:
            if m.can_act():
                action = m.choose_action()
                result = action()

                if isinstance(result, str):
                    ui.log(result, "info")
                else:
                    damage, msg, crit = result
                    if damage > 0:
                        p.hp -= damage
                        tag = "monster_crit" if crit else "monster_hit"
                        ui.log(msg, tag)

                        if p.hp <= 0:
                            p.hp = 0
                            ui.log("You were defeated!", "defeat")
                            state["in_combat"] = False
                            ui.disable_actions()

        root.after(200, monster_ai_tick)

    # ---------------------------------------------------------
    # TRAINING POINT ALLOCATION
    # ---------------------------------------------------------
    def on_allocate_stat(stat_name):
        p = state["player"]

        if p.allocate_stat(stat_name):
            ui.log(f"You increased {stat_name}!", "info")

        # Still have points? Keep prompting
        if p.training_points > 0:
            ui.show_training_prompt(p, on_allocate_stat)
            return

        # No points left → close training UI and resume game
        ui.hide_training_prompt()   # <-- THIS is the missing piece
        ui.enable_actions()
        state["in_combat"] = True   # <-- Resume combat loop


    def handle_level_up():
        p = state["player"]
        if p.training_points > 0:
            ui.disable_actions()
            ui.show_training_prompt(p, on_allocate_stat)

    # ---------------------------------------------------------
    # PLAYER ACTION HANDLER
    # ---------------------------------------------------------
    def handle_action(action_name):
        if not state["in_combat"]:
            return

        p = state["player"]
        m = state["monster"]

        if action_name in ("lunge", "slash", "draw", "rage_slash"):
            if action_name == "lunge":
                damage, msg, crit = p.class_obj.lunge(p)
            elif action_name == "slash":
                damage, msg, crit = p.class_obj.slash(p)
            elif action_name == "draw":
                damage, msg, crit = p.class_obj.draw(p)
            else:
                damage, msg, crit = p.class_obj.rage_slash(p)

            if damage > 0 and m is not None:
                m.hp -= damage
                tag = "crit" if crit else "player_hit"
                ui.log(msg, tag)

                if m.hp <= 0:
                    m.hp = 0
                    ui.log("You defeated the monster!", "victory")
                    state["in_combat"] = False
                    ui.disable_actions()

                    xp, gold, rare = generate_loot(m)
                    leveled = p.gain_xp(xp)
                    p.gold += gold

                    loot_msg = f"You gain {xp} XP and {gold} gold."
                    ui.log(loot_msg, "loot")
                    if rare:
                        ui.log(f"You found: {rare}", "loot")

                    if leveled:
                        ui.log("You leveled up!", "levelup")
                        handle_level_up()
                    else:
                        ui.show_fight_prompt()

                    return
            else:
                ui.log(msg, "info")

        elif action_name == "advance":
            msg = p.advance()
            ui.log(msg, "info")

        elif action_name == "retreat":
            msg = p.retreat()
            ui.log(msg, "info")

        elif action_name == "flee":
            msg = p.flee(m)
            ui.log(msg, "info")
            if "successfully fled" in msg:
                state["in_combat"] = False
                ui.disable_actions()
                ui.show_fight_prompt()

        elif action_name == "potion":
            msg = p.use_potion()
            ui.log(msg, "info")

    # ---------------------------------------------------------
    # FIGHT-ANOTHER / REST FLOW
    # ---------------------------------------------------------
    def on_fight_another():
        new_monster = generate_monster(player.level)
        state["monster"] = new_monster
        state["in_combat"] = True
        ui.set_monster(new_monster)
        ui.hide_fight_prompt()
        ui.enable_actions()
        ui.log(f"A new {new_monster} appears!", "info")

    def on_stop():
        state["in_combat"] = False
        ui.hide_fight_prompt()
        ui.disable_actions()
        ui.log("You decide to rest.", "info")
        ui.show_rest_prompt()

    def on_rest_continue():
        msg = state["player"].save()
        ui.log(msg, "info")
        ui.log("You feel rested.", "info")

        new_monster = generate_monster(state["player"].level)
        state["monster"] = new_monster
        ui.set_monster(new_monster)

        state["in_combat"] = True
        ui.hide_rest_prompt()
        ui.enable_actions()
        ui.log(f"A new {new_monster} approaches!", "info")

    def on_rest_exit():
        root.destroy()

    def on_rest_save():
        msg = state["player"].save()
        ui.log(msg, "info")
        ui.log("Progress saved while resting.", "info")


    # ---------------------------------------------------------
    # UI SETUP
    # ---------------------------------------------------------
    ui = GameUI(
        root,
        player,
        monster,
        handle_action,
        on_fight_another,
        on_stop,
        on_rest_continue,
        on_rest_exit
    )

    ui.log(f"A wild {monster} appears!", "info")

    # ---------------------------------------------------------
    # REGEN TICK
    # ---------------------------------------------------------
    def regen_tick():
        player.regen(state["in_combat"])
        root.after(5000, regen_tick)

    regen_tick()
    monster_ai_tick()
    root.mainloop()


if __name__ == "__main__":
    main()
