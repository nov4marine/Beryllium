import arcade
import arcade.gui
from arcade.gui import UIAnchorLayout

class GenericMenu(UIAnchorLayout):
    def __init__(self, title="Menu Title"):
        super().__init__(size_hint=(0.7, 0.7))
        self.with_background(color=arcade.color.DARK_SLATE_GRAY)

        # Title bar
        self.top_bar = UIAnchorLayout(size_hint=(1, 0.08))
        self.top_bar.with_background(color=arcade.color.DARK_BLUE_GRAY)
        self.title_label = arcade.gui.UILabel(text=title, font_size=18)
        self.close_button = arcade.gui.UIFlatButton(text="X", size_hint=(0.08, 0.8))
        self.close_button.on_click = self.close_window

        self.top_bar.add(self.title_label, anchor_x="center")
        self.top_bar.add(self.close_button, anchor_x="right")
        self.add(self.top_bar, anchor_y="top")

        # Content area
        self.content_frame = UIAnchorLayout(size_hint=(1, 0.92))
        self.content_frame.with_background(color=arcade.color.CHARCOAL)
        self.add(self.content_frame, anchor_y="bottom")

    def close_window(self, event=None):
        print("Closing menu")
        self.visible = False  # Or remove from parent
        #self.parent.remove(self)  # If you want to remove it from the UI manager
        # Ideally probably have 1 of every menu and just show/hide and update content as needed, instead of creating/destroying them

    def open_window(self):
        self.visible = True
