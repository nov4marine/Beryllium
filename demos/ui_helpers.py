import arcade
import arcade.gui

"""My first time using standalone helper functions. These are just small functions to create common UI elements
with less boilerplate code. For example, making a label with a background color."""


# 1. Widget Factory Functions

def make_label(text, size=12, bold=False, color=arcade.color.WHITE, bg=None):
    label = arcade.gui.UILabel(text=text, font_size=size, bold=bold, text_color=color)
    if bg:
        label.with_background(color=bg)
    return label

def make_box(vertical=True, size_hint=(1, 1), bg=None, border=None, space_between=10):
    box = arcade.gui.UIBoxLayout(vertical=vertical, size_hint=size_hint, space_between=space_between)
    if bg:
        box.with_background(color=bg)
    if border:
        box.with_border(color=border)
    return box

# 2. Reuseable info panels

def make_stats_box(stats: dict):
    box = make_box(vertical=False, size_hint=(1, 0.1), bg=(30, 30, 30, 180), space_between=50)
    for key, value in stats.items():
        box.add(make_label(f"{key}: {value}"))
    return box