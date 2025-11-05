from random import randint

from pyglet.math import Vec2

import arcade
from arcade import Sprite, SpriteList, open_window
from arcade.gui import UIDummy, UILayout, UIView
from arcade.gui.widgets import W


class WorldSpaceLayout(UILayout):
    def __init__(self, world_cam: arcade.Camera2D, size_hint=(1, 1), **kwargs):
        super().__init__(size_hint=size_hint, **kwargs)
        self.world_cam = world_cam

    # Override add to use world_position instead of position
    def add(self, child: W, world_position=Vec2(0, 0), **kwargs) -> W:
        return super().add(child, position=world_position, **kwargs)

    # Place children based on their world position
    def do_layout(self):
        for child, data in self._children:
            wpos = data["position"]
            sx, sy = self.world_cam.project(wpos)
            child.rect = child.rect.align_center((sx, sy))


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

        self.world_layout = self.add_widget(WorldSpaceLayout(self.world_cam))

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
            self.world_layout.add(UIDummy(width=90, height=32), world_position=Vec2(wx, wy))

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
