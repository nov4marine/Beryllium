from random import randint
from typing import Optional

from pyglet.math import Vec2

import arcade
from arcade import Sprite, SpriteList, open_window
from arcade.gui import UIEvent, UIKeyEvent, UIView, UIWidget


class CustomWidget(UIWidget):
    def __init__(self, wold_cam: arcade.Camera2D, wpos: Vec2):
        super().__init__(width=90, height=40)
        self.world_cam = wold_cam
        self.wpos = wpos
        self.with_background(color=arcade.uicolor.GREEN_GREEN_SEA)

    def on_update(self, dt):
        # calculate screen coords
        sx, sy = self.world_cam.project(self.wpos)
        self.rect = self.rect.align_center((sx, sy))

    def on_event(self, event: UIEvent) -> Optional[bool]:
        if isinstance(event, UIKeyEvent):
            print("CustomWidget got event", event)

        return super().on_event(event)


class MyView(UIView):
    def __init__(self):
        super().__init__()

        self.background_color = arcade.color.BLACK

        self.world_cam = arcade.Camera2D()

        self.sprites = SpriteList()

        for _ in range(100):
            self.sprites.append(
                Sprite(
                    ":resources:/logo.png",
                    center_x=randint(0, 2000),
                    center_y=randint(0, 2000),
                    scale=0.1,
                )
            )

    def on_mouse_drag(
        self, x: int, y: int, dx: int, dy: int, _buttons: int, _modifiers: int
    ) -> bool | None:
        if _buttons == arcade.MOUSE_BUTTON_MIDDLE:
            wx, wy = self.world_cam.position
            self.world_cam.position = wx - dx, wy - dy

        return True

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> bool | None:
        if button == arcade.MOUSE_BUTTON_LEFT:
            wx, wy, _ = self.world_cam.unproject((x, y))
            widget = CustomWidget(self.world_cam, Vec2(wx, wy))
            self.add_widget(widget)

    def on_draw_before_ui(self):
        with self.world_cam.activate():
            self.sprites.draw()

    def on_draw_after_ui(self):
        pass


if __name__ == "__main__":
    open_window(window_title="Minimal example", width=1280, height=720, resizable=True).show_view(
        MyView()
    )
    arcade.run()
