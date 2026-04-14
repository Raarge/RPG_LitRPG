import tkinter as tk
from tkinter import ttk
import time
from engine.distance import Distance
import json
import os

class GameUI:
    def __init__(
        self,
        root,
        player,
        monster,
        on_action,
        on_fight_another,
        on_stop,
        on_rest_continue=None,
        on_rest_exit=None
    ):
        self.root = root
        self.player = player
        self.monster = monster

        self.on_action = on_action
        self.on_fight_another = on_fight_another
        self.on_stop = on_stop

        # NEW
        self.on_rest_continue = on_rest_continue
        self.on_rest_exit = on_rest_exit

        #self.build_ui()


        # ---------------------------------------------------------
        # WINDOW CONFIGURATION
        # ---------------------------------------------------------
        root.title("RPG Combat UI")
        root.geometry("1300x900")
        root.minsize(1200, 850)

        # Grid expansion rules
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=2)
        root.grid_rowconfigure(2, weight=1)   # Combat log expands
        root.grid_rowconfigure(6, minsize=60) # Spacer row before actions

        # ---------------------------------------------------------
        # LEFT COLUMN — PLAYER INFO
        # ---------------------------------------------------------

        # Player Stats
        stats_frame = ttk.LabelFrame(root, text="Player Stats")
        stats_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nw")

        self.stat_labels = {}
        row = 0
        for stat in ["STR", "DEX", "CON", "INT", "WIS", "DISPELL"]:
            label = ttk.Label(stats_frame, text=f"{stat}: 0")
            label.grid(row=row, column=0, sticky="w")
            self.stat_labels[stat] = label
            row += 1

        # Player HP
        hp_frame = ttk.LabelFrame(root, text="Player HP")
        hp_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nw")

        self.hp_label = ttk.Label(hp_frame, text="HP: 0/0")
        self.hp_label.grid(row=0, column=0, sticky="w")

        self.hp_bar = ttk.Progressbar(hp_frame, length=260)
        self.hp_bar.grid(row=1, column=0, pady=5)

        # Stamina
        stamina_frame = ttk.LabelFrame(root, text="Stamina")
        stamina_frame.grid(row=2, column=0, padx=15, pady=5, sticky="nw")

        self.stamina_label = ttk.Label(stamina_frame, text="Stamina: 0/0")
        self.stamina_label.grid(row=0, column=0, sticky="w")

        self.stamina_bar = ttk.Progressbar(stamina_frame, length=260)
        self.stamina_bar.grid(row=1, column=0, pady=5)

        # Level & XP
        level_frame = ttk.LabelFrame(root, text="Level & XP")
        level_frame.grid(row=3, column=0, padx=15, pady=5, sticky="nw")

        self.level_label = ttk.Label(level_frame, text="Level: 1")
        self.level_label.grid(row=0, column=0, sticky="w")

        self.xp_bar = ttk.Progressbar(level_frame, length=260)
        self.xp_bar.grid(row=1, column=0, pady=5)

        # Distance & Cooldown
        dc_frame = ttk.LabelFrame(root, text="Distance & Cooldown")
        dc_frame.grid(row=4, column=0, padx=15, pady=5, sticky="nw")

        self.distance_label = ttk.Label(dc_frame, text="Distance: Ranged")
        self.distance_label.grid(row=0, column=0, sticky="w")

        self.cooldown_label = ttk.Label(dc_frame, text="Ready")
        self.cooldown_label.grid(row=1, column=0, sticky="w")

        # ---------------------------------------------------------
        # RIGHT COLUMN — MONSTER + SKILLS + COMBAT LOG
        # ---------------------------------------------------------

        # Monster Info (HP hidden)
        monster_frame = ttk.LabelFrame(root, text="Monster")
        monster_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nw")

        self.monster_label = ttk.Label(monster_frame, text="")
        self.monster_label.grid(row=0, column=0, sticky="w")

        # Skills Panel
        skills_frame = ttk.LabelFrame(root, text="Skills")
        skills_frame.grid(row=1, column=1, padx=15, pady=10, sticky="nw")

        self.skill_labels = {}
        self.skill_bars = {}
        row = 0
        for skill_name, skill in player.class_obj.skills.items():
            label = ttk.Label(skills_frame, text=f"{skill_name}: Lvl {skill.level}")
            label.grid(row=row, column=0, sticky="w")
            self.skill_labels[skill_name] = label

            bar = ttk.Progressbar(skills_frame, length=260)
            bar.grid(row=row, column=1, padx=5, pady=2)
            self.skill_bars[skill_name] = bar
            row += 1

        # ---------------------------------------------------------
        # COMBAT LOG — FULL HEIGHT COLUMN
        # ---------------------------------------------------------
        log_frame = ttk.LabelFrame(root, text="Combat Log")
        log_frame.grid(row=2, column=1, rowspan=3, padx=15, pady=10, sticky="nsew")

        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(1, weight=2)

        self.log_box = tk.Text(
            log_frame,
            width=80,
            height=30,
            state="disabled",
            wrap="word",
            bg="black",
            fg="white"
        )
        self.log_box.grid(row=0, column=0, sticky="nsew")

        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_box["yscrollcommand"] = scrollbar.set

        # Log color tags
        self.log_box.tag_config("info", foreground="white")
        self.log_box.tag_config("player_hit", foreground="white")
        self.log_box.tag_config("crit", foreground="red")
        self.log_box.tag_config("monster_hit", foreground="orange")
        self.log_box.tag_config("monster_crit", foreground="red")
        self.log_box.tag_config("victory", foreground="green")
        self.log_box.tag_config("defeat", foreground="red")
        self.log_box.tag_config("loot", foreground="cyan")
        self.log_box.tag_config("levelup", foreground="yellow")

        # ---------------------------------------------------------
        # ACTION BUTTONS — PUSHED FAR DOWN
        # ---------------------------------------------------------
        buttons_frame = ttk.LabelFrame(root, text="Actions")
        buttons_frame.grid(row=7, column=0, columnspan=2, padx=15, pady=25, sticky="ew")

        ttk.Button(buttons_frame, text="Lunge", command=lambda: self.on_action("lunge")).grid(row=0, column=0, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Slash", command=lambda: self.on_action("slash")).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Draw", command=lambda: self.on_action("draw")).grid(row=0, column=2, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Rage Slash", command=lambda: self.on_action("rage_slash")).grid(row=0, column=3, padx=10, pady=5)

        ttk.Button(buttons_frame, text="Advance", command=lambda: self.on_action("advance")).grid(row=1, column=0, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Retreat", command=lambda: self.on_action("retreat")).grid(row=1, column=1, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Flee", command=lambda: self.on_action("flee")).grid(row=1, column=2, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Use Potion", command=lambda: self.on_action("potion")).grid(row=1, column=3, padx=10, pady=5)

        ttk.Button(buttons_frame, text="Save Game", command=self.save_game).grid(row=2, column=0, padx=10, pady=5)
        ttk.Button(buttons_frame, text="Load Game", command=self.load_game).grid(row=2, column=1, padx=10, pady=5)


        self.buttons_frame = buttons_frame

        # ---------------------------------------------------------
        # FIGHT-ANOTHER PROMPT — BELOW ACTIONS
        # ---------------------------------------------------------
        prompt_frame = ttk.Frame(root)
        prompt_frame.grid(row=8, column=0, columnspan=2, pady=10)
        self.prompt_frame = prompt_frame

        self.prompt_label = ttk.Label(prompt_frame, text="Fight another?")
        self.prompt_yes = ttk.Button(prompt_frame, text="Yes", command=self.on_fight_another)
        self.prompt_no = ttk.Button(prompt_frame, text="No", command=self.on_stop)

        self.rest_continue_btn = ttk.Button(
        self.prompt_frame, text="Continue", command=self.on_rest_continue
        )

        self.rest_exit_btn = ttk.Button(
            self.prompt_frame, text="Exit Game", command=self.on_rest_exit
        )



        self.hide_fight_prompt()

        # Start UI updates
        self.update_ui()

    # ---------------------------------------------------------
    # LOGGING
    # ---------------------------------------------------------
    def log(self, message, tag="info"):
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    # ---------------------------------------------------------
    # MONSTER UPDATE
    # ---------------------------------------------------------
    def set_monster(self, monster):
        self.monster = monster

    # ---------------------------------------------------------
    # FIGHT ANOTHER PROMPT
    # ---------------------------------------------------------
    def show_fight_prompt(self):
        self.prompt_label.grid(row=0, column=0, padx=10)
        self.prompt_yes.grid(row=0, column=1, padx=10)
        self.prompt_no.grid(row=0, column=2, padx=10)

    def hide_fight_prompt(self):
        for w in self.prompt_frame.winfo_children():
            w.grid_remove()

    # ---------------------------------------------------------
    # ENABLE / DISABLE ACTIONS
    # ---------------------------------------------------------
    def disable_actions(self):
        for child in self.buttons_frame.winfo_children():
            child.config(state="disabled")

    def enable_actions(self):
        for child in self.buttons_frame.winfo_children():
            child.config(state="normal")

    # ---------------------------------------------------------
    # UI UPDATE LOOP
    # ---------------------------------------------------------
    def update_ui(self):
        stats = self.player.stats()
        for stat, label in self.stat_labels.items():
            label.config(text=f"{stat}: {stats[stat]}")

        self.hp_label.config(text=f"HP: {int(self.player.hp)}/{self.player.max_hp}")
        self.hp_bar["value"] = (self.player.hp / self.player.max_hp) * 100

        self.stamina_label.config(text=f"Stamina: {self.player.stamina}/{self.player.max_stamina}")
        self.stamina_bar["value"] = (self.player.stamina / self.player.max_stamina) * 100

        self.level_label.config(text=f"Level: {self.player.level}")
        self.xp_bar["value"] = (self.player.xp / self.player.xp_required) * 100

        self.distance_label.config(text=f"Distance: {Distance.names[self.player.distance]}")

        if self.player.can_act():
            self.cooldown_label.config(text="Ready")
        else:
            remaining = max(0, int(self.player.cooldown_until - time.time()))
            self.cooldown_label.config(text=f"Cooldown: {remaining}s")

        for name, skill in self.player.class_obj.skills.items():
            self.skill_labels[name].config(text=f"{name}: Lvl {skill.level}")
            percent = (skill.xp / skill.xp_required) * 100
            self.skill_bars[name]["value"] = percent

        if self.monster:
            self.monster_label.config(text=f"{self.monster}")
        else:
            self.monster_label.config(text="No enemy")

        self.root.after(200, self.update_ui)

    def show_rest_prompt(self):
        self.prompt_label.config(text="Rest complete. Continue?")
        self.prompt_label.grid(row=0, column=0, padx=10)
        self.rest_continue_btn.grid(row=0, column=1, padx=10)
        self.rest_exit_btn.grid(row=0, column=2, padx=10)

    def hide_rest_prompt(self):
        for w in self.prompt_frame.winfo_children():
            w.grid_remove()

    def save_game(self):
        data = self.player.to_dict()

        filename = f"{self.player.class_obj.name}.json"
        path = os.path.join(os.getcwd(), filename)

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        self.log(f"Game saved to {filename}", "info")


    def load_game(self):
        filename = f"{self.player.class_obj.name}.json"
        path = os.path.join(os.getcwd(), filename)

        if not os.path.exists(path):
            self.log("No save file found.", "info")
            return

        with open(path, "r") as f:
            data = json.load(f)

        self.player.from_dict(data)

        # Refresh UI immediately
        self.update_ui()
        self.log("Game loaded successfully.", "info")

