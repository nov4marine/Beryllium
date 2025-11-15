"""
BEHOLD! THE MAGICAL PYGAME SURFACE! 
This file will contain by attempt at roughly mimicking the pygame surface concept but in Arcade.
Template used is: arcade.create_text_sprite()
"""

import arcade
from arcade.exceptions import PerformanceWarning, warning
from arcade.resources import resolve
from arcade.texture_atlas import TextureAtlasBase
from arcade.types import Color, Point, RGBOrA255
from arcade.types.rect import LRBT, Rect

class Surface:
    """A not so simple surface class to mimic pygame surfaces using Arcade sprites."""
    def __init__(self):
        pass

    @staticmethod
    def draw_surface(self, drawing, name, size):
        """Draw the surface and its contents."""
        object = drawing

        texture = arcade.Texture.create_empty(name, size)

        if not texture_atlas:
            texture_atlas = arcade.get_window().ctx.default_atlas
        texture_atlas.add(texture)
        with texture_atlas.render_into(texture) as fbo:
            fbo.clear(color=arcade.color.TRANSPARENT_BLACK)
            object.draw()

        return arcade.Sprite(
            texture,
            center_x=object.right - (size[0] / 2),
            center_y=object.top,
        )

    @staticmethod
    def create_text_sprite(
        text: str,
        color: RGBOrA255 = arcade.color.WHITE,
        font_size: float = 12.0,
        width: int | None = None,
        align: str = "left",
        font_name = ("calibri", "arial"),
        bold: bool | str = False,
        italic: bool = False,
        anchor_x: str = "left",
        multiline: bool = False,
        texture_atlas: TextureAtlasBase | None = None,
        background_color: RGBOrA255 | None = None,
    ) -> arcade.Sprite:
        text_object = arcade.Text(
            text,
            x=0,
            y=0,
            color=color,
            font_size=font_size,
            width=width,
            align=align,
            font_name=font_name,
            bold=bold,
            italic=italic,
            anchor_x=anchor_x,
            anchor_y="baseline",
            multiline=multiline,
        )

        size = (
            int(text_object.right - text_object.left),
            int(text_object.top - text_object.bottom),
        )
        text_object.y = -text_object.bottom
        texture = arcade.Texture.create_empty(text, size)

        if not texture_atlas:
            texture_atlas = arcade.get_window().ctx.default_atlas
        texture_atlas.add(texture)
        with texture_atlas.render_into(texture) as fbo:
            fbo.clear(color=background_color or arcade.color.TRANSPARENT_BLACK)
            text_object.draw()

        return arcade.Sprite(
            texture,
            center_x=text_object.right - (size[0] / 2),
            center_y=text_object.top,
        )