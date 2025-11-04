"""
Style Shuffler — Text-Only Edition (Blush Pink Theme)
--------------------------------------------------------
Shuffle outfit components as TEXT only — no images required.

Features:
- Categories: tops, bottoms, shoes, accessories, colour_palette, weather, activity
- Shuffle Outfit / Reshuffle per category / Lock toggle
- Save Look → appends to exports/looks.csv
- Copy Look → copies current selection to clipboard
"""

import csv
import random
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------------
# COLOUR PALETTE (Blush + White)
# ---------------------------
BG_COLOUR = "#F7DDE5"       # soft blush background
CARD_COLOUR = "#FFFFFF"     # white tiles
TEXT_COLOUR = "#333333"     # dark grey text
BUTTON_COLOUR = "#E9C3CF"   # muted rose button
BUTTON_HOVER = "#F4BFCF"    # lighter blush hover tone

# ---------------------------
# Configurable data
# ---------------------------
DATA = {
    "tops": [
        "White tee", "Black tank", "Denim shirt", "Silk cami",
        "Graphic tee", "Cropped hoodie", "Button-up", "Mesh long-sleeve",
    ],
    "bottoms": [
        "Blue jeans", "Black wide-leg", "Denim skirt", "Pleated mini",
        "Cargo pants", "Tailored trousers", "Satin slip skirt",
    ],
    "shoes": [
        "White sneakers", "Black boots", "Strappy heels", "Loafers",
        "Platform sandals", "Ballet flats",
    ],
    "accessories": [
        "Gold hoops", "Silver chain", "Baseball cap", "Mini baguette bag",
        "Crossbody bag", "Sunglasses", "Hair ribbon",
    ],
    "colour_palette": [
        "Monochrome", "Neon pop", "Earth tones", "Pastels",
        "Warm metallics", "Cool minimal", "Jewel tones",
    ],
    "weather": [
        "Hot & sunny", "Warm", "Mild", "Windy",
        "Cool", "Cold", "Rainy", "Stormy",
    ],
    "activity": [
        "Uni day", "Office casual", "Date night", "Festival",
        "Beach walk", "Gym to brunch", "Dinner with friends", "Errands",
    ],
}

CATEGORIES = list(DATA.keys())
EXPORTS_DIR = Path("exports")
CSV_FILE = EXPORTS_DIR / "looks.csv"


# ---------------------------
# Model layer
# ---------------------------
@dataclass
class Selection:
    value: str | None = None
    locked: bool = False


class StyleModel:
    def __init__(self, data):
        self.data = data
        self.state = {cat: Selection() for cat in data}

    def random_choice(self, cat):
        return random.choice(self.data.get(cat, [])) if self.data.get(cat) else None

    def reshuffle(self, cat):
        if self.state[cat].locked:
            return
        self.state[cat].value = self.random_choice(cat)

    def shuffle_all(self):
        for cat in self.data:
            self.reshuffle(cat)

    def toggle_lock(self, cat):
        sel = self.state[cat]
        sel.locked = not sel.locked
        return sel.locked

    def clear_locks(self):
        for sel in self.state.values():
            sel.locked = False

    def as_dict(self):
        return {cat: self.state[cat].value for cat in self.data}


# ---------------------------
# Tkinter UI
# ---------------------------
class StyleShufflerApp(ttk.Frame):
    def __init__(self, master, model):
        super().__init__(master)
        self.model = model
        self.pack(fill="both", expand=True)
        self.master.configure(bg=BG_COLOUR)

        self.value_labels = {}
        self.lock_vars = {}

        self._build_header()
        self._build_grid()
        self._build_footer()

        self.model.shuffle_all()
        self._render_all()

    # ---------- UI ----------
    def _build_header(self):
        header = tk.Frame(self, bg=BG_COLOUR)
        header.pack(side="top", fill="x", padx=12, pady=12)

        tk.Label(
            header,
            text="Style Shuffler",
            font=("Helvetica", 20, "bold"),
            bg=BG_COLOUR,
            fg=TEXT_COLOUR,
        ).pack(side="left")

        btnrow = tk.Frame(header, bg=BG_COLOUR)
        btnrow.pack(side="right")

        self._mk_button(btnrow, "Shuffle Outfit", self._shuffle_all).pack(side="left", padx=6)
        self._mk_button(btnrow, "Clear Locks", self._clear_locks).pack(side="left", padx=6)
        self._mk_button(btnrow, "Copy Look", self._copy_to_clipboard).pack(side="left", padx=6)
        self._mk_button(btnrow, "Save Look", self._save_look).pack(side="left", padx=6)

    def _build_grid(self):
        grid = tk.Frame(self, bg=BG_COLOUR)
        grid.pack(fill="both", expand=True, padx=12, pady=6)

        for i, cat in enumerate(CATEGORIES):
            frame = tk.LabelFrame(
                grid,
                text=cat.replace("_", " ").capitalize(),
                bg=CARD_COLOUR,
                fg=TEXT_COLOUR,
                labelanchor="n",
                font=("Helvetica", 12, "bold"),
                bd=1,
                relief="solid",
                highlightbackground=BUTTON_COLOUR,
                highlightthickness=1,
                padx=10,
                pady=8,
            )
            frame.grid(row=i // 2, column=i % 2, sticky="nsew", padx=8, pady=8)
            grid.columnconfigure(i % 2, weight=1)

            val = tk.Label(frame, text="—", bg=CARD_COLOUR, fg=TEXT_COLOUR, font=("Helvetica", 13))
            val.pack(fill="x", pady=(4, 8))
            self.value_labels[cat] = val

            controls = tk.Frame(frame, bg=CARD_COLOUR)
            controls.pack(fill="x", pady=(0, 4))

            self._mk_button(controls, "Reshuffle", lambda c=cat: self._reshuffle_one(c)).pack(side="left")
            lock_var = tk.BooleanVar(value=False)
            self.lock_vars[cat] = lock_var
            tk.Checkbutton(
                controls,
                text="Lock",
                variable=lock_var,
                command=lambda c=cat: self._toggle_lock(c),
                bg=CARD_COLOUR,
                fg=TEXT_COLOUR,
                selectcolor=BUTTON_HOVER,
                activebackground=CARD_COLOUR,
            ).pack(side="left", padx=10)

    def _build_footer(self):
        foot = tk.Frame(self, bg=BG_COLOUR)
        foot.pack(side="bottom", fill="x", padx=12, pady=8)
        tk.Label(
            foot,
            text="Tip: Edit the DATA lists to customise items.",
            bg=BG_COLOUR,
            fg="#666666",
            font=("Helvetica", 10),
        ).pack(side="left")

    # ---------- Button helper ----------
    def _mk_button(self, parent, text, command):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=BUTTON_COLOUR,
            fg=TEXT_COLOUR,
            activebackground=BUTTON_HOVER,
            activeforeground=TEXT_COLOUR,
            font=("Helvetica", 11, "bold"),
            relief="flat",
            padx=6,
            pady=2,
        )
        btn.bind("<Enter>", lambda e: e.widget.config(bg=BUTTON_HOVER))
        btn.bind("<Leave>", lambda e: e.widget.config(bg=BUTTON_COLOUR))
        return btn

    # ---------- Actions ----------
    def _reshuffle_one(self, cat):
        self.model.reshuffle(cat)
        self._render(cat)

    def _shuffle_all(self):
        self.model.shuffle_all()
        self._render_all()

    def _toggle_lock(self, cat):
        desired = self.lock_vars[cat].get()
        current = self.model.state[cat].locked
        if desired != current:
            self.model.toggle_lock(cat)
        self._render(cat)

    def _clear_locks(self):
        self.model.clear_locks()
        for var in self.lock_vars.values():
            var.set(False)
        self._render_all()

    def _save_look(self):
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = {"timestamp": timestamp, **self.model.as_dict()}
        write_header = not CSV_FILE.exists()
        with CSV_FILE.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", *CATEGORIES])
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        messagebox.showinfo("Saved", f"Look saved to {CSV_FILE}")

    def _copy_to_clipboard(self):
        items = [
            f"{cat.replace('_',' ').capitalize()}: {self.model.state[cat].value or '—'}"
            for cat in CATEGORIES
        ]
        text = "\n".join(items)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Current look copied to clipboard.")

    # ---------- Rendering ----------
    def _render(self, cat):
        sel = self.model.state[cat]
        label = self.value_labels[cat]
        display = sel.value or "(no option)"
        if sel.locked:
            display = f"🔒 {display}"
        label.configure(text=display)

    def _render_all(self):
        for cat in CATEGORIES:
            self._render(cat)


# ---------------------------
# App bootstrap
# ---------------------------
def main():
    root = tk.Tk()
    root.title("Style Shuffler — Blush Edition")
    root.geometry("780x680")

    model = StyleModel(DATA)
    _ = StyleShufflerApp(root, model)

    root.mainloop()


if __name__ == "__main__":
    main()
